import cbpro.messenger

from cbpro.utils import get_time_intervals
from time import sleep


class Products(cbpro.messenger.Subscriber):
    def list(self) -> list:
        return self.messenger.get('/products')

    def get(self, product_id: str) -> dict:
        return self.messenger.get(f'/products/{product_id}')

    def order_book(self, product_id: str, params: dict = None) -> dict:
        # NOTE:
        #   - This request is not paginated
        #   - Polling is discouraged for this method
        #   - Use the websocket stream for polling instead
        # https://docs.pro.coinbase.com/#get-product-order-book
        endpoint = f'/products/{product_id}/book'
        return self.messenger.get(endpoint, params=params)

    def ticker(self, product_id: str) -> dict:
        # NOTE:
        #   - Polling is discouraged for this method
        #   - Use the websocket stream for polling instead
        return self.messenger.get(f'/products/{product_id}/ticker')

    def trades(self, product_id: str, params: dict = None) -> list:
        return self.messenger.paginate(f'/products/{product_id}/trades', params=params)

    def history(self, product_id: str, params: dict = None) -> list:
        # NOTE:
        #   - Polling is discouraged for this method
        #   - Use the websocket stream for polling instead
        endpoint = f'/products/{product_id}/candles'
        return self.messenger.get(endpoint, params=params)

    def stats(self, product_id: str) -> dict:
        return self.messenger.get(f'/products/{product_id}/stats')


class History(cbpro.messenger.Subscriber):
    def candles(self, product_id: str, params: dict = None):
        """Get all candles for a given time frame from params.start to params.end.

        If the requested time range is too large, the request is separated into multiple time intervals.
        """
        endpoint = f"/products/{product_id}/candles"

        all_candles = []
        loop_params = params.copy()
        for start, end in get_time_intervals(params):
            loop_params["start"] = start
            loop_params["end"] = end
            candles = self.messenger.get(endpoint, params=loop_params)
            all_candles += candles

            # sleep 0.26 seconds to prevent a timeout because a rate limit of 4 requests/second
            sleep(0.26)

        # sort by time ascending
        all_candles.sort(key=lambda candle: candle[0])

        return all_candles


class Currencies(cbpro.messenger.Subscriber):
    def list(self) -> list:
        # NOTE: Not all currencies may be currently in use for trading
        return self.messenger.get('/currencies')

    def get(self, currency_id: str) -> dict:
        # NOTE: Currencies which have or had no representation in ISO 4217
        # may use a custom code
        return self.messenger.get(f'/currencies/{currency_id}')


class Time(cbpro.messenger.Subscriber):
    def get(self) -> dict:
        # NOTE: This endpoint does not require authentication
        # NOTE: The epoch field represents decimal seconds since Unix Epoch
        return self.messenger.get('/time')


class PublicClient(object):
    def __init__(self, messenger: cbpro.messenger.Messenger) -> None:
        self.products = Products(messenger)
        self.currencies = Currencies(messenger)
        self.time = Time(messenger)
        self.history = History(messenger)


def public_client(url=None):
    messenger = cbpro.messenger.Messenger(url=url)
    return PublicClient(messenger)
