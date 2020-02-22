import requests
import pickle
import logging
import json

logging.basicConfig(level=logging.DEBUG)

class ProxyCollector:
    def __init__(self, filename, dont_init=False):
        self.filename = filename+ '.pkl'
        self.proxies = {
                "help":"This is a dict saving me['proxies']['ip:port'/'status'/'status_for_projects']. ",
                "proxies": []
            }
        
        if dont_init:
            logging.warning(' Not init pickle. Will get clean `self.proxies` and it might overwrite the old pickle. Make sure you are using clean pickle file for testing.')
        else:
            self.init_pickle()
    
    def init_pickle(self):
        logging.info(" init pickle (will load self.proxies)")
        try:
            with open(self.filename, 'rb') as f:
                self.proxies = pickle.load(f)
        except FileNotFoundError as e:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.proxies, f)

    def get_my_ip(self, proxy=None):
        # """NOTE: Proxy need to be full path (http://xxx.xxx.xxx.xxx:xxxx) """
        if proxy == None:
            pass
        else:
            proxy = self.format_proxy_with_http(proxy)
            proxy = {
                'http': proxy,
                'https': proxy,
            }
        req = requests.get('https://api.ipify.org?format=json',proxies=proxy)
        req_json = json.loads(req.text)
        logging.debug("My {} is: {}".format('IP', req_json['ip']))
        return req_json['ip']
    
    def format_proxy_with_http(self, proxy):
        if proxy.startswith('http://'):
            return proxy
        else:
            return "http://{}".format(proxy)

    def collect_raw_proxy(self, url):
        proxy_list = requests.get(url).text.split('\n')
        for proxy in proxy_list:
            try:
                ip = self.get_my_ip(proxy=proxy)
                logging.info(' Proxy worked. IP: {}'.format(ip))
                self.add_proxy(proxy, status='alive')
            except requests.exceptions.ProxyError as e :
                logging.info(' {} proxy not working...'.format(proxy))
        return


    def add_proxy(self, proxy, status="unknown", status_for_projects="unknown", save_pickle=True):
        
        if not any([proxy == p['ip:port'] for p in self.proxies['proxies']]):
            proxy = {
                'ip:port': proxy,
                'status': status,
                'status_for_projects': status_for_projects    
            }
            self.proxies['proxies'].append(proxy)
        else:
            proxy = next(prox for prox in self.proxies['proxies'] if prox['ip:port'] == proxy)
            proxy['status'] = status
            proxy['status_for_projects'] = status_for_projects

        if save_pickle == True:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.proxies, f)
            logging.debug(" Add proxy and SAVED to picke.")
        else:
            logging.debug(" Add proxy but NOT SAVING to pickle.")
        logging.debug('Add Proxy to proxies[\'proxies\']')

    def print_proxy_in_pickle(self):
        try:
            with open(self.filename, 'rb') as f:
                self.proxies = pickle.load(f)
            for proxy in self.proxies['proxies']:
                print("[*] {} is {}".format(proxy['ip:port'], proxy['status']))

        except FileNotFoundError as e:
            logging.debug(e)
            print("[*] {} not found. must be a new file? There is nothing to print.")
    def return_alive_proxy(self, test=False):
        # TODO: Test proxies before return.
        alive_proxies = []
        for proxy in self.proxies['proxies']:
            if proxy['status'] == 'alive':
                alive_proxies.append(proxy)
        return alive_proxies

        
if __name__ == '__main__':
    proxyman = ProxyCollector(filename='testing')
    print('IP: {}'.format(proxyman.get_my_ip()))
    proxyman.print_proxy_in_pickle()
    # proxyman.collect_raw_proxy(url="https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt")
    


