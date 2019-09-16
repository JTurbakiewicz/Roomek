import os
if '/home/RoomekBot' in os.path.abspath(''):
    from Scraper.PropertyScraper.spiders import olx_spider_main, olx_room_spider
else:
   from Scraper.PropertyScraper.spiders import olx_spider_main, olx_room_spider, otodom_spider_main
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
import sys
from six.moves.configparser import ConfigParser
from tokens import scraping_python_path

def closest_scrapy_cfg(path='.', prevpath=None):
    """Return the path to the closest scrapy.cfg file by traversing the current
    directory and its parents
    """
    if path == prevpath:
        return ''
    path = os.path.abspath(path)
    cfgfile = os.path.join(path, 'scrapy.cfg')
    if os.path.exists(cfgfile):
        return cfgfile
        #return r"C:\Users\Artur\Desktop\CODE\roBOT\Scraper\scrapy.cfg"  #TODO
    return closest_scrapy_cfg(os.path.dirname(path), path)
    #return r"C:\Users\Artur\Desktop\CODE\roBOT\Scraper\scrapy.cfg" #TODO

def get_sources(use_closest=True):
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
        os.path.expanduser('~/.config')
    sources = ['/etc/scrapy.cfg', r'c:\scrapy\scrapy.cfg',
               xdg_config_home + '/scrapy.cfg',
               os.path.expanduser('~/.scrapy.cfg')]
    if use_closest:
        sources.append(closest_scrapy_cfg(scraping_python_path))
    return sources

def get_config(use_closest=True):
    """Get Scrapy config file as a SafeConfigParser"""
    sources = get_sources(use_closest)
    cfg = ConfigParser()
    cfg.read(sources)
    return cfg

def init_env(project='default', set_syspath=True):
    """Initialize environment to use command-line tool from inside a project
    dir. This sets the Scrapy settings module and modifies the Python path to
    be able to locate the project module.
    """
    cfg = get_config()
    if cfg.has_option('settings', project):
        os.environ['SCRAPY_SETTINGS_MODULE'] = cfg.get('settings', project)
    closest = closest_scrapy_cfg(scraping_python_path)
    if closest:
        projdir = os.path.dirname(closest)
        if set_syspath and projdir not in sys.path:
            sys.path.append(projdir)

def get_project_settings():

    project = os.environ.get('SCRAPY_PROJECT', 'default')
    init_env(project)

    settings = Settings()
    settings_module_path = os.environ.get(ENVVAR)
    if settings_module_path:
        settings.setmodule(settings_module_path, priority='project')

    # XXX: remove this hack
    pickled_settings = os.environ.get("SCRAPY_PICKLED_SETTINGS_TO_OVERRIDE")
    if pickled_settings:
        settings.setdict(pickle.loads(pickled_settings), priority='project')

    # XXX: deprecate and remove this functionality
    env_overrides = {k[7:]: v for k, v in os.environ.items() if
                     k.startswith('SCRAPY_')}
    if env_overrides:
        settings.setdict(env_overrides, priority='project')

    return settings

ENVVAR = 'SCRAPY_SETTINGS_MODULE'

s = get_project_settings()

configure_logging(settings=s, install_root_handler=False)
runner = CrawlerRunner(s)

base_string = 'https://www.olx.pl/nieruchomosci'
housing_types = ['mieszkania', 'stancje-pokoje']
business_types = ['sprzedaz', 'wynajem']
cities = ['warszawa', 'krakow', 'lodz', 'wroclaw', 'poznan', 'gdansk', 'szczecin', 'bydgoszcz', 'lublin', 'bialystok']
#cities = ['warszawa']
urls_flats_OLX = []
urls_rooms_OLX = []

for type in housing_types:
    for city in cities:
        if type == 'mieszkania':
            for purpose in business_types:
                urls_flats_OLX.append('/'.join([base_string,type,purpose,city,'']))
        elif type == 'stancje-pokoje':
            urls_rooms_OLX.append('/'.join([base_string, type, city, '']))

@defer.inlineCallbacks
def crawl():
    #yield runner.crawl(olx_room_spider.OlxRoomSpider, urls_to_scrape=urls_rooms_OLX)
    yield runner.crawl(olx_spider_main.OlxSpiderMain, urls_to_scrape = urls_flats_OLX)
    #yield runner.crawl(otodom_spider_main.OtodomSpiderMain, urls_to_scrape = urls_flats_OLX)
    reactor.stop()

crawl()
reactor.run()  # the script will block here until the last crawl call is finished
