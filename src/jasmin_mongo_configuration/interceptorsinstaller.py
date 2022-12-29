import pickle as pickle
from twisted.internet import reactor, defer
from jasmin.routing.proxies import RouterPBProxy
from jasmin.routing.Interceptors import DefaultInterceptor
from jasmin.routing.jasminApi import MTInterceptorScript, MOInterceptorScript
from jasmin_mongo_configuration.defaults import *

import pkg_resources


class InterceptorsInstaller:
    def __init__(
        self,
        host: str = DEFAULT_JASMIN_HOST,
        port: int = DEFAULT_ROUTER_PB_PROXY_PORT,
        username: str = DEFAULT_ROUTER_PB_PROXY_USERNAME,
        password: str = DEFAULT_ROUTER_PB_PROXY_PASSWORD
    ):
        self.host: str = host
        self.port: int = port
        self.username: str = username
        self.password: str = password

        self.MtInterceptorScript = pkg_resources.resource_string(
            __name__, 'interceptors/mt.py')
        self.MoInterceptorScript = pkg_resources.resource_string(
            __name__, 'interceptors/mo.py')

        self.runScenario()
        reactor.run()

    @defer.inlineCallbacks
    def runScenario(self):
        try:
            proxy_router = RouterPBProxy()
            yield proxy_router.connect(self.host, self.port, self.username, self.password)

            yield proxy_router.mtinterceptor_flush()

            yield proxy_router.mtinterceptor_add(DefaultInterceptor(MTInterceptorScript(self.MtInterceptorScript)), 0)
            yield proxy_router.mointerceptor_add(DefaultInterceptor(MOInterceptorScript(self.MoInterceptorScript)), 0)
            listMtInterceptors = yield proxy_router.mtinterceptor_get_all()
            listMoInterceptors = yield proxy_router.mointerceptor_get_all()
            listMtInterceptors = pickle.loads(listMtInterceptors)
            listMoInterceptors = pickle.loads(listMoInterceptors)

        except Exception as e:
            print("ERROR RUNNING SCENARIO: %s" % str(e))
        finally:
            reactor.stop()
