import json
from enum import Enum
import requests
from typing import Optional, List


class SolanaMintAddresses:

    USDC_MAINNET_BETA = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    MANGO_MAINNET_BETA = "MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac"
    SERUM_MAINNET_BETA = "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt"
    RAYDIUM_MAINNET_BETA = "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R"
    WRAPPED_SOL_MAINNET_BETA = "So11111111111111111111111111111111111111112"
    ATLAS_MAINNET_BETA = "ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx"

    # Make a pull request and add more! That would be cool.


class SolanaNetwork(Enum):
    DEVNET = "devnet"
    MAINNET_BETA = "mainnet-beta"


class SolanaCurrencyUnit(Enum):
    LAMPORT = "lamport"
    SOL = "sol"


class SolanaNFTUploadMethod(Enum):
    S3 = "S3"
    LINK = "LINK"


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
            'APISecretKey': self.__api_secret_key,
            'Language': 'Python'
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
                params=payload,
                headers=headers,
                timeout=120
            )
        else:
            r = requests.request(
                request_method.value,
                url=self.__url + endpoint,
                data=payload,
                files=files,
                headers=headers,
                timeout=120
            )
        try:
            json_content = json.loads(r.content)
        except json.decoder.JSONDecodeError:
            return r
        return json_content

    def get_api_activity_history(self) -> dict:
        """
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
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGenerateSecretRecoveryPhrase
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
        derivation_path: Optional[str] = None,
        passphrase: str = str()
    ) -> str:
        """
        Derives a public key given the info.
        More info:
        https://docs.theblockchainapi.com/#operation/solanaDerivePublicKey
        :param secret_recovery_phrase:
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :return:
        """
        payload = {
            "secret_recovery_phrase": secret_recovery_phrase,
            "passphrase": passphrase
        }
        if derivation_path is not None:
            payload["derivation_path"] = derivation_path

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
        network: SolanaNetwork = SolanaNetwork.DEVNET,
        mint_address: str = None
    ) -> dict:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetBalance
        :param public_key:
        :param unit: Ignored if `mint_address` provided
        :param network:
        :param mint_address:
        :return:
        """
        payload = {
            "public_key": public_key,
            "unit": unit.value,
            "network": network.value
        }
        if mint_address is not None:
            payload['mint_address'] = mint_address

        response = self._request(
            payload=payload,
            endpoint="solana/wallet/balance",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_wallet_token_holdings(
        self,
        public_key: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ) -> list:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetTokensBelongingToWallet
        :param public_key:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/wallet/{network.value}/{public_key}/tokens",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['nfts_owned']

    def get_nfts_belonging_to_address(
        self,
        public_key: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ) -> list:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetNFTsBelongingToWallet
        :param public_key:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/wallet/{network.value}/{public_key}/nfts",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['nfts_owned']

    def get_is_candy_machine(
        self,
        public_key: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetAccountIsCandyMachine
        :param public_key:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/account/{network.value}/{public_key}/is_candy_machine",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['is_candy_machine']

    def get_is_nft(
        self,
        public_key: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetAccountIsNFT
        :param public_key:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/account/{network.value}/{public_key}/is_nft",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['is_nft']

    def get_nft_owner(
        self,
        mint_address: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        response = self._request(
            payload=dict(),
            endpoint=f"solana/nft/{network.value}/{mint_address}/owner",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['nft_owner']

    def get_associated_token_account_address(
        self,
        mint_address: str,
        public_key: str
    ) -> str:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaDeriveAssociatedTokenAccountAddress
        :param mint_address: The mint address of the NFT or SPL token
        :param public_key: The public key of the account that owns the associated token account address
        :return:
        """
        payload = {
            "mint_address": mint_address,
            "public_key": public_key
        }

        response = self._request(
            payload=payload,
            endpoint=f"solana/wallet/{public_key}/associated_token_account/{mint_address}",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['associated_token_address']

    def transfer(
        self,
        secret_recovery_phrase: str,
        recipient_address: str,
        token_address: Optional[str] = None,
        derivation_path: Optional[str] = None,
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET,
        amount: str = "1"
    ) -> str:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaTransfer
        :param secret_recovery_phrase:
        :param recipient_address:
        :param token_address: If not provided, defaults to transferring SOL
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :param network:
        :param amount:
        :return:
        """
        payload = {
            "recipient_address": recipient_address,
            "secret_recovery_phrase": secret_recovery_phrase,
            "passphrase": passphrase,
            "network": network.value,
            "amount": amount
        }
        if derivation_path is not None:
            payload['derivation_path'] = derivation_path
        if token_address is not None:
            payload["token_address"] = token_address

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
        derivation_path: Optional[str] = None,
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET,
        nft_name: str = str(),
        nft_symbol: str = str(),
        nft_description: str = str(),
        nft_url: str = str(),
        nft_metadata: Optional[dict] = None,
        nft_upload_method: SolanaNFTUploadMethod = SolanaNFTUploadMethod.S3,
        creators: Optional[List[str]] = None,
        share: Optional[List[int]] = None,
        seller_fee_basis_points: int = 0,
        is_mutable: bool = True,
        is_master_edition: bool = True
    ) -> dict:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaCreateNFT
        :param secret_recovery_phrase:
        :param derivation_path: Derivation path default matches the CLI. Use "m/44/501/0/0" to match Phantom.
        :param passphrase:
        :param network:
        :param nft_name: The name of the NFT
        :param nft_symbol: The symbol of the NFT
        :param nft_description: The description of the NFT
        :param nft_url: The image of the NFT
        :param nft_metadata: The metadata of the NFT
        :param nft_upload_method: The upload method of the NFT. Upload the URL to S3 and embed it. Or save it directly
        to the NFT
        :param creators:
        :param share:
        :param seller_fee_basis_points:
        :param is_mutable:
        :param is_master_edition:
        :return:
        """
        if nft_metadata is None:
            nft_metadata = dict()
        payload = {
            "secret_recovery_phrase": secret_recovery_phrase,
            "passphrase": passphrase,
            "network": network.value,
            "nft_name": nft_name,
            "nft_symbol": nft_symbol,
            "nft_metadata": nft_metadata,
            "nft_description": nft_description,
            "nft_url": nft_url,
            "nft_upload_method": nft_upload_method.value,
            "is_mutable": is_mutable,
            "is_master_edition": is_master_edition,
            "seller_fee_basis_points": seller_fee_basis_points
        }
        if derivation_path is not None:
            payload['derivation_path'] = derivation_path
        if creators is not None:
            payload['creators'] = json.dumps(creators)
        if share is not None:
            payload['share'] = json.dumps(share)

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
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetNFT
        :param mint_address:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/nft/{network.value}/{mint_address}",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_nft_mint_fee(
        self
    ) -> dict:
        """
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetNFTMintFee
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

    def get_airdrop(
        self,
        recipient_address: str
    ) -> str:
        """
        Get an airdrop of 0.015 SOL on the devnet
        More info:
        https://docs.theblockchainapi.com/#operation/solanaGetAirdrop
        :param recipient_address:
        :return: Transaction signature
        """
        response = self._request(
            payload={
                "recipient_address": recipient_address
            },
            endpoint="solana/wallet/airdrop",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['transaction_signature']

    def get_candy_machine_info(
        self,
        candy_machine_id: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        More Info:
        https://docs.theblockchainapi.com/#operation/solanaGetCandyMachineDetails
        :param candy_machine_id:
        :param network:
        :return:
        """
        payload = {
            "network": network.value,
            "candy_machine_id": candy_machine_id
        }
        response = self._request(
            payload=payload,
            endpoint="solana/nft/candy_machine/info",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def mint_from_candy_machine(
        self,
        config_address: str,
        secret_recovery_phrase: str,
        derivation_path: Optional[str] = None,
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        Mint Info:
        https://docs.theblockchainapi.com/#operation/solanaMintFromCandyMachine
        :param config_address: The config address of the candy machine.
        You can retrieve this if you have the candy machine ID using
        this endpoint (https://docs.theblockchainapi.com/#operation/solanaGetCandyMachineDetails)
        and retrieving the config_address from the response..
        :param secret_recovery_phrase:
        :param derivation_path:
        :param passphrase:
        :param network:
        :return: A task_id. Use the `get_task` function to retrieve the result once this task has completed processing.
        You can poll the `get_task` function to see results.
        """
        payload = {
            "secret_recovery_phrase": secret_recovery_phrase,
            "network": network.value,
            "passphrase": passphrase,
            "config_address": config_address
        }
        if derivation_path is not None:
            payload['derivation_path'] = derivation_path
        response = self._request(
            payload=payload,
            endpoint="solana/nft/candy_machine/mint",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['task_id']

    def create_test_candy_machine(
        self,
        secret_recovery_phrase: str,
        derivation_path: Optional[str] = None,
        passphrase: str = str(),
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        Mint Info:
        https://docs.theblockchainapi.com/#operation/solanaCreateTestCandyMachine
        :param secret_recovery_phrase:
        :param derivation_path:
        :param passphrase:
        :param network:
        :return:
        """
        payload = {
            "secret_recovery_phrase": secret_recovery_phrase,
            "network": network.value,
            "passphrase": passphrase
        }
        if derivation_path is not None:
            payload['derivation_path'] = derivation_path
        response = self._request(
            payload=payload,
            endpoint="solana/nft/candy_machine",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['candy_machine_address']

    def get_task(self, task_id: str):
        """
        More Info:
        https://docs.theblockchainapi.com/#operation/getTask
        :param task_id:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"task/{task_id}",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_solana_transaction(
        self,
        tx_signature: str,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        https://docs.theblockchainapi.com/#operation/solanaGetTransaction
        :param tx_signature:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/transaction/{network.value}/{tx_signature}",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_config_details(
        self,
        config_address,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        https://docs.theblockchainapi.com/#operation/solanaGetCandyMachineConfigurationDetails
        :param config_address:
        :param network:
        :return:
        """
        payload = {
            "network": network.value,
            "config_address": config_address
        }
        response = self._request(
            payload=payload,
            endpoint="solana/nft/candy_machine/config/info",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_nfts_minted_from_candy_machine(
        self,
        candy_machine_id,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        https://docs.theblockchainapi.com/#operation/solanaGetNFTsMintedFromCandyMachine
        :param candy_machine_id:
        :param network:
        :return:
        """
        payload = {
            "network": network.value,
            "candy_machine_id": candy_machine_id
        }
        response = self._request(
            payload=payload,
            endpoint="solana/nft/candy_machine/nfts",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_candy_machine_id_from_nft(
        self,
        mint_address,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        https://docs.theblockchainapi.com/#operation/solanaGetNFTsCandyMachineId
        :param mint_address:
        :param network:
        :return:
        """
        payload = {
            "network": network.value,
            "mint_address": mint_address
        }
        response = self._request(
            payload=payload,
            endpoint="solana/nft/candy_machine_id",
            request_method=self.__RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['candy_machine_id']

    def get_account_info(
        self,
        public_key,
        network: SolanaNetwork = SolanaNetwork.DEVNET
    ):
        """
        https://docs.theblockchainapi.com/#operation/solanaGetAccount
        :param public_key:
        :param network:
        :return:
        """
        response = self._request(
            payload=dict(),
            endpoint=f"solana/account/{network.value}/{public_key}",
            request_method=self.__RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response
