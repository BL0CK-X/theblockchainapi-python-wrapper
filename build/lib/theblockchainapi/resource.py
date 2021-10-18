import json
from enum import Enum
import requests
from typing import Optional


class SolanaNetwork(Enum):
    DEVNET = "devnet"
    MAINNET_BETA = "mainnet-beta"


class SolanaCurrencyUnit(Enum):
    LAMPORT = "lamport"
    SOL = "sol"


class TheBlockchainAPIResource:

    __url = "https://api.theblockchainapi.com/v1/"

    class __RequestMethod(Enum):
        GET = "GET"
        POST = "POST"
        PATCH = "PATCH"
        DELETE = "DELETE"

    def __init__(self, api_key_id: str, api_secret_key: str):
        """

        To get an API key pair, go to https://dashboard.theblockchainapi.com/.

        Sign in and then click on the "API KEYS" tab.

        :param api_key_id: Your API key ID
        :param api_secret_key: Your API secret key
        """
        self.__api_key_id = api_key_id
        self.__api_secret_key = api_secret_key

    def _get_headers(self):
        """
        Get the headers with the appropriate authentication parameters
        :return: The headers
        """
        return {
            'APIKeyID': self.__api_key_id,
            'APISecretKey': self.__api_secret_key
        }

    def _request(self, payload, endpoint, request_method, files=None, headers=None):
        """
        Makes an API request.
        :param payload: the payload containing the parameters
        :param endpoint: the desired endpoint
        :param request_method: the method (e.g. POST, GET, PATCH, DELETE)
        :param files: files to send. only used when changing a profile image
        :param headers: headers for the request. only specified when changing a profile image
        :return:
        """
        if headers is None:
            headers = self._get_headers()

        if files is None:
            r = requests.request(
                request_method.value,
                url=self.__url + endpoint,
                data=json.dumps(payload),
                headers=headers
            )
        else:
            r = requests.request(
                request_method.value,
                url=self.__url + endpoint,
                data=payload,
                files=files,
                headers=headers
            )
        try:
            json_content = json.loads(r.content)
        except json.decoder.JSONDecodeError:
            return r
        return json_content

    def get_api_activity_history(self) -> dict:
        """
        https://docs.theblockchainapi.com/#tag/Activity/paths/~1v1~1account~1activity/get
        :return: The API activity history
        """
        response = self._request(
            payload=dict(),
            endpoint="account/activity",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise response['error_message']
        return response

    def generate_secret_key(self) -> str:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-Wallet/paths/~1v1~1solana~1wallet~1secret_recovery_phrase/post
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint="solana/wallet/secret_recovery_phrase",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['secret_recovery_phrase']

    def derive_public_key(
        self,
        secret_recovery_phrase: str,
        derivation_path: str = "m/44/501/0/0",
        passphrase: str = str()
    ) -> str:
        """
        Derives a public key given the info.
        More info: https://docs.theblockchainapi.com/#tag/Solana-Wallet/paths/~1v1~1solana~1wallet~1public_key/post
        :param secret_recovery_phrase:
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :return:
        """
        payload = {
            "secret_recovery_phrase": secret_recovery_phrase,
            "derivation_path": derivation_path,
            "passphrase": passphrase
        }

        response = self._request(
            payload=payload,
            endpoint="solana/wallet/public_key",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['public_key']

    def get_balance(
        self,
        public_key: str,
        unit: SolanaCurrencyUnit = SolanaCurrencyUnit.LAMPORT,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ) -> dict:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-Wallet/paths/~1v1~1solana~1wallet~1balance/get
        :param public_key:
        :param unit:
        :param network:
        :return:
        """
        payload = {
            "public_key": public_key,
            "unit": unit.value,
            "network": network.value
        }

        response = self._request(
            payload=payload,
            endpoint="solana/wallet/balance",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_nfts_belonging_to_address(
        self,
        public_key: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ) -> list:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-Wallet/paths/~1v1~1solana~1wallet~1nfts/get
        :param public_key:
        :param network:
        :return:
        """
        payload = {
            "public_key": public_key,
            "network": network.value
        }

        response = self._request(
            payload=payload,
            endpoint="solana/wallet/nfts",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['nfts_owned']

    def derive_associated_token_account_address(
        self,
        token_address: str,
        secret_recovery_phrase: str,
        derivation_path: str = "m/44/501/0/0",
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ) -> str:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-Wallet/paths/~1v1~1solana~1wallet~1associated_token_account/post
        :param token_address:
        :param secret_recovery_phrase:
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :param network:
        :return:
        """
        payload = {
            "token_address": token_address,
            "secret_recovery_phrase": secret_recovery_phrase,
            "derivation_path": derivation_path,
            "passphrase": passphrase,
            "network": network.value
        }

        response = self._request(
            payload=payload,
            endpoint="solana/wallet/associated_token_account",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['associated_token_address']

    def transfer(
        self,
        token_address: str,
        recipient_address: str,
        secret_recovery_phrase: str,
        derivation_path: str = "m/44/501/0/0",
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET,
        amount: str = "1"
    ) -> str:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-Wallet/paths/~1v1~1solana~1wallet~1transfer/post
        :param token_address:
        :param recipient_address:
        :param secret_recovery_phrase:
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :param network:
        :param amount:
        :return:
        """
        payload = {
            "token_address": token_address,
            "recipient_address": recipient_address,
            "secret_recovery_phrase": secret_recovery_phrase,
            "derivation_path": derivation_path,
            "passphrase": passphrase,
            "network": network.value,
            "amount": amount
        }

        response = self._request(
            payload=payload,
            endpoint="solana/wallet/transfer",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['transaction_signature']

    def create_nft(
        self,
        secret_recovery_phrase: str,
        derivation_path: str = "m/44/501/0/0",
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET,
        nft_name: str = str(),
        nft_symbol: str = str(),
        nft_description: str = str(),
        nft_url: str = str(),
        nft_metadata: dict = None
    ) -> dict:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-NFT/paths/~1v1~1solana~1nft/post
        :param secret_recovery_phrase:
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :param network:
        :param nft_name: The name of the NFT
        :param nft_symbol: The symbol of the NFT
        :param nft_description: The description of the NFT
        :param nft_url: The image of the NFT
        :param nft_metadata: The metadata of the NFT
        :return:
        """
        if nft_metadata is None:
            nft_metadata = dict()
        payload = {
            "secret_recovery_phrase": secret_recovery_phrase,
            "derivation_path": derivation_path,
            "passphrase": passphrase,
            "network": network.value,
            "nft_name": nft_name,
            "nft_symbol": nft_symbol,
            "nft_description": nft_description,
            "nft_url": nft_url,
            "nft_metadata": nft_metadata
        }

        response = self._request(
            payload=payload,
            endpoint="solana/nft",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_nft_metadata(
        self,
        mint_address: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ) -> dict:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-NFT/paths/~1v1~1solana~1nft/get
        :param mint_address:
        :param network:
        :return:
        """
        payload = {
            "mint_address": mint_address,
            "network": network.value
        }

        response = self._request(
            payload=payload,
            endpoint="solana/nft",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_nft_mint_fee(
        self
    ) -> dict:
        """
        More info: https://docs.theblockchainapi.com/#tag/Solana-NFT/paths/~1v1~1solana~1nft~1mint~1fee/get
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint="solana/nft/mint/fee",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response
