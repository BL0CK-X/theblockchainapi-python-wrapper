from typing import Optional, List, Union
from theblockchainapi.resource import APIResource
from enum import Enum


class CurrencyUnit:

    class SolanaCurrencyUnit(Enum):
        LAMPORT = "lamport"
        SOL = "sol"

    class EthereumCurrencyUnit(Enum):
        WEI = "wei"
        GWEI = "gwei"
        ETH = "ether"


class Wallet:

    def __init__(
        self,
        secret_recovery_phrase: str = None,
        private_key: List[int] = None,
        b58_private_key: str = None,
        hex_private_key: str = None,
        derivation_path: Union[str] = None,
        passphrase: str = str()
    ):

        supplied = int(secret_recovery_phrase is not None) + int(private_key is not None) \
                   + int(b58_private_key is not None) + int(hex_private_key is not None)

        if supplied != 1:
            raise Exception(
                "Provide EXACTLY ONE of "
                "`secret_recovery_phrase` OR "
                "`private_key` OR "
                "`b58_private_key` OR "
                "`hex_private_key`."
            )
        if secret_recovery_phrase is not None and not isinstance(secret_recovery_phrase, str):
            raise Exception("`secret_recovery_phrase` must be a `str`.")
        elif private_key is not None and not isinstance(private_key, list):
            raise Exception(
                "`private_key` must be a `list`. Example: [99, 110, 111, ..., 88, 88, 17]. "
                "If you are trying to provide a `str` private key from Phantom, use the argument "
                "`b58_private_key`"
            )
        elif b58_private_key is not None and not isinstance(b58_private_key, str):
            raise Exception("`b58_private_key` must be a `str`.")
        elif hex_private_key is not None and not isinstance(hex_private_key, str):
            raise Exception("`hex_private_key` must be a `str`.")

        self.secret_recovery_phrase = secret_recovery_phrase
        self.private_key = private_key
        self.b58_private_key = b58_private_key
        self.hex_private_key = hex_private_key

        if derivation_path is not None:
            if not isinstance(derivation_path, str):
                raise Exception("`derivation_path` must be a `str`.")
        if passphrase is not None:
            if not isinstance(passphrase, str):
                raise Exception("`passphrase` must be a `str`.")

        self.derivation_path = derivation_path
        self.passphrase = passphrase

    def get_formatted_request_payload(self) -> dict:
        if self.secret_recovery_phrase is not None:
            wallet = {
                'secret_recovery_phrase': self.secret_recovery_phrase
            }
            if self.derivation_path is not None:
                wallet['derivation_path'] = self.derivation_path
            if self.passphrase is not None:
                wallet['passphrase'] = self.passphrase
            return {
                'wallet': wallet
            }
        elif self.private_key is not None:
            return {
                'wallet': {
                    'private_key': self.private_key
                }
            }
        elif self.b58_private_key is not None:
            return {
                'wallet': {
                    'b58_private_key': self.b58_private_key
                }
            }
        elif self.hex_private_key is not None:
            return {
                'wallet': {
                    'hex_private_key': self.hex_private_key
                }
            }
        else:
            raise Exception("Unknown error. Improperly initialized instance of `SolanaWallet`.")


class Blockchain(Enum):

    AVALANCHE = "avalanche"
    BINANCE = "binance_smart_chain"
    ETHEREUM = "ethereum"
    SOLANA = "solana"
    NEAR = "near"


class AvalancheChain(Enum):
    X = "X"
    P = "P"
    C = "C"


class BlockchainNetwork:

    class SolanaNetwork(Enum):
        DEVNET = "devnet"
        MAINNET_BETA = "mainnet-beta"

    class EthereumNetwork(Enum):
        ROPSTEN = "ropsten"
        MAINNET = "mainnet"

    class BinanceNetwork(Enum):
        TESTNET = "testnet"
        MAINNET = "mainnet"

    class AvalancheNetwork(Enum):
        TESTNET = "testnet"
        MAINNET = "mainnet"

    class NearNetwork(Enum):
        TESTNET = "testnet"
        MAINNET = "mainnet"


class BlockchainAPIResource(APIResource):

    def __init__(
        self,
        api_key_id: str,
        api_secret_key: str,
        blockchain: Union[Blockchain, str],
        network: Union[
            BlockchainNetwork.SolanaNetwork,
            BlockchainNetwork.EthereumNetwork,
            BlockchainNetwork.BinanceNetwork,
            BlockchainNetwork.AvalancheNetwork,
            BlockchainNetwork.NearNetwork,
            str
        ],
        avalanche_chain: Optional[AvalancheChain] = None,
        timeout=None
    ):

        super().__init__(api_key_id=api_key_id, api_secret_key=api_secret_key, timeout=timeout)

        if isinstance(blockchain, str):
            try:
                blockchain = Blockchain(blockchain)
            except (TypeError, ValueError):
                raise Exception(f"Invalid value for `blockchain`: `{blockchain}`.")
        elif not isinstance(blockchain, Blockchain):
            raise Exception(
                "Unknown type provided for `blockchain`. "
                "Must be either `str` or `Blockchain`. "
                "See `from theblockchainapi.api_resource import Blockchain`. "
            )

        if blockchain.value == Blockchain.AVALANCHE.value:
            if avalanche_chain is None:
                raise Exception(
                    "Provide value for `avalanche_chain`. "
                    "Must be either `str` or `AvalancheChain`. "
                    "See `from theblockchainapi.api_resource import AvalancheChain`. "
                    "Example: `AvalancheChain.X`."
                )
            elif isinstance(avalanche_chain, str):
                try:
                    avalanche_chain = AvalancheChain(avalanche_chain)
                except (TypeError, ValueError):
                    raise Exception(f"Invalid value for `avalanche_chain`: `{avalanche_chain}`.")
            elif not isinstance(avalanche_chain, AvalancheChain):
                raise Exception(
                    "Unknown type provided for `avalanche_chain`. "
                    "Must be either `str` or `AvalancheChain`. "
                    "See `from theblockchainapi.api_resource import AvalancheChain`. "
                    "Example: `AvalancheChain.X`."
                )

        if isinstance(network, BlockchainNetwork.SolanaNetwork):
            if blockchain.value != Blockchain.SOLANA.value:
                raise Exception(
                    "You must use `Blockchain.SOLANA` if you are going to use `BlockchainNetwork.SolanaNetwork`."
                )
        elif isinstance(network, BlockchainNetwork.AvalancheNetwork):
            if blockchain.value != Blockchain.AVALANCHE.value:
                raise Exception(
                    "You must use `Blockchain.AVALANCHE` if you are going to use `BlockchainNetwork.AvalancheNetwork`."
                )
        elif isinstance(network, BlockchainNetwork.EthereumNetwork):
            if blockchain.value != Blockchain.ETHEREUM.value:
                raise Exception(
                    "You must use `Blockchain.ETHEREUM` if you are going to use `BlockchainNetwork.EthereumNetwork`."
                )
        elif isinstance(network, BlockchainNetwork.NearNetwork):
            if blockchain.value != Blockchain.NEAR.value:
                raise Exception(
                    "You must use `Blockchain.NEAR` if you are going to use `BlockchainNetwork.NearNetwork`."
                )
        elif isinstance(network, BlockchainNetwork.BinanceNetwork):
            if blockchain.value != Blockchain.BINANCE.value:
                raise Exception(
                    "You must use `Blockchain.BINANCE` if you are going to use `BlockchainNetwork.BinanceNetwork`."
                )
        elif isinstance(network, str):
            if blockchain.value == Blockchain.SOLANA.value:
                try:
                    network = BlockchainNetwork.SolanaNetwork(network)
                except Exception:
                    raise Exception(
                        "Invalid value for `network`. Use the `enum`, `Blockchain.Network.SolanaNetwork`."
                    )
            elif blockchain.value == Blockchain.AVALANCHE.value:
                try:
                    network = BlockchainNetwork.AvalancheNetwork(network)
                except Exception:
                    raise Exception(
                        "Invalid value for `network`. Use the `enum`, `Blockchain.Network.AvalancheNetwork`."
                    )
            elif blockchain.value == Blockchain.NEAR.value:
                try:
                    network = BlockchainNetwork.NearNetwork(network)
                except Exception:
                    raise Exception(
                        "Invalid value for `network`. Use the `enum`, `Blockchain.Network.NearNetwork`."
                    )
            elif blockchain.value == Blockchain.ETHEREUM.value:
                try:
                    network = BlockchainNetwork.EthereumNetwork(network)
                except Exception:
                    raise Exception(
                        "Invalid value for `network`. Use the `enum`, `Blockchain.Network.EthereumNetwork`."
                    )
            elif blockchain.value == Blockchain.BINANCE.value:
                try:
                    network = BlockchainNetwork.BinanceNetwork(network)
                except Exception:
                    raise Exception(
                        "Invalid value for `network`. Use the `enum`, `Blockchain.Network.BinanceNetwork`."
                    )
            else:
                raise NotImplementedError
        else:
            raise Exception(
                "Invalid type for `network`. "
                "See the class `from theblockchainapi.api_resource import Network`. "
                "Example of usage: `Network.SolanaNetwork.DEV_NET` or `Network.EthereumNetwork.MAINNET`."
            )

        self.blockchain: Blockchain = blockchain
        self.avalanche_chain: AvalancheChain = avalanche_chain
        self.network: Union[
            BlockchainNetwork.AvalancheNetwork,
            BlockchainNetwork.BinanceNetwork,
            BlockchainNetwork.EthereumNetwork,
            BlockchainNetwork.NearNetwork,
            BlockchainNetwork.SolanaNetwork,
        ] = network

    def get_rpc_url(
        self
    ) -> str:
        return f"{self._url}/{self.blockchain.value}/{self.network.value}/rpc"

    def make_rpc_request(
        self,
        method: str,
        params: object
    ) -> str:
        response = self._request(
            endpoint=self.get_rpc_url(),
            payload={
                'method': method,
                'params': params
            },
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    # -------------------------------------------------------------------------------------------- BEGIN: WALLET

    def generate_seed_phrase(
        self
    ) -> str:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/generateSeedPhrase
        """
        response = self._request(
            payload=dict(),
            endpoint=f"{self.blockchain.value}/wallet/generate/secret_recovery_phrase",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['secret_recovery_phrase']

    def generate_private_key(
        self
    ) -> dict:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/generatePrivateKey
        """
        response = self._request(
            payload=dict(),
            endpoint=f"{self.blockchain.value}/wallet/generate/private_key",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def derive_blockchain_identifier(
        self,
        wallet: Wallet
    ) -> str:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/derivePrivateKey
        """

        response = self._request(
            payload=wallet.get_formatted_request_payload(),
            endpoint=f"{self.blockchain.value}/wallet/identifier",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])

        if self.blockchain.value == Blockchain.SOLANA.value:
            return response['public_key']
        elif self.blockchain.value == Blockchain.NEAR.value:
            return response['hex_public_key']
        elif self.blockchain.value == Blockchain.AVALANCHE.value \
                and self.avalanche_chain.value != AvalancheChain.C.value:
            return response['bech_public_address']
        else:
            return response['hex_public_address']

    def derive_private_key(
        self,
        wallet: Wallet
    ) -> str:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/deriveWalletIdentifier
        """
        response = self._request(
            payload=wallet.get_formatted_request_payload(),
            endpoint=f"{self.blockchain.value}/wallet/private_key",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_balance(
        self,
        blockchain_identifier: str,
        unit: Optional[Union[CurrencyUnit.SolanaCurrencyUnit, CurrencyUnit.EthereumCurrencyUnit, str]] = None,
        token_blockchain_identifier: str = None
    ) -> dict:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/getBalance
        """
        payload = {
            "blockchain_identifier": blockchain_identifier,
            "network": self.network.value
        }
        if unit is not None:

            if not isinstance(unit, CurrencyUnit.SolanaCurrencyUnit) \
                    and not isinstance(unit, CurrencyUnit.EthereumCurrencyUnit) \
                    and not isinstance(unit, str):

                raise Exception(
                    "Invalid type for `unit`. "
                    "See the class `from theblockchainapi.api_resource import CurrencyUnit`. "
                    "Example of usage: `CurrencyUnit.SolanaCurrencyUnit.SOL`."
                )

            if isinstance(unit, str):
                payload['unit'] = unit
            else:
                payload['unit'] = unit.value

        if token_blockchain_identifier is not None:
            payload['token_blockchain_identifier'] = token_blockchain_identifier

        response = self._request(
            payload=payload,
            endpoint=f"{self.blockchain.value}/wallet/balance",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def transfer(
        self,
        wallet: Optional[Wallet],
        recipient_blockchain_identifier: str,
        token_blockchain_identifier: Optional[str] = None,
        amount: str = "1",
        fee_payer_wallet: Optional[Wallet] = None,
        sender_blockchain_identifier: Optional[str] = None,
        return_compiled_transaction: bool = False
    ) -> dict:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/transfer
        """
        payload = dict()

        if wallet is not None:
            payload = wallet.get_formatted_request_payload()

        payload["network"] = self.network.value
        payload["amount"] = amount
        payload["recipient_blockchain_identifier"] = recipient_blockchain_identifier
        payload["return_compiled_transaction"] = return_compiled_transaction

        if sender_blockchain_identifier is not None:
            payload["sender_blockchain_identifier"] = sender_blockchain_identifier

        if token_blockchain_identifier is not None:
            payload["token_blockchain_identifier"] = token_blockchain_identifier

        if fee_payer_wallet is not None:
            payload["fee_payer_wallet"] = fee_payer_wallet.get_formatted_request_payload()['wallet']

        response = self._request(
            payload=payload,
            endpoint=f"{self.blockchain.value}/wallet/transfer",
            request_method=self._RequestMethod.POST
        )

        if 'error_message' in response:
            raise Exception(response['error_message'])

        return response

    def get_airdrop(
        self,
        recipient_address: str
    ) -> str:
        """
        https://docs.blockchainapi.com/#tag/Wallet/operation/getAirdrop
        """
        response = self._request(
            payload={
                "recipient_blockchain_identifier": recipient_address
            },
            endpoint=f"{self.blockchain.value}/wallet/airdrop",
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['transaction_blockchain_identifier']

    # -------------------------------------------------------------------------------------------- END: WALLET

    # -------------------------------------------------------------------------------------------- BEGIN: TRANSACTION

    def get_transaction(
        self,
        transaction_blockchain_identifier: str
    ):
        """
        https://docs.blockchainapi.com/#tag/Transaction/operation/getTransaction
        """
        url = f"{self.blockchain.value}/" \
              f"transaction/" \
              f"{self.network.value}/" \
              f"{transaction_blockchain_identifier}"
        response = self._request(
            endpoint=url,
            request_method=self._RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    # -------------------------------------------------------------------------------------------- END: TRANSACTION

    # -------------------------------------------------------------------------------------------- BEGIN: NAME SERVICE

    def get_name_from_blockchain_identifier(self, token_blockchain_identifier: str):
        url = f"{self.blockchain.value}/" \
              f"{self.network.value}/" \
              f"name_service/blockchain_identifier_to_name"
        response = self._request(
            endpoint=url,
            payload={
                'blockchain_identifier': token_blockchain_identifier
            },
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['name']

    def get_blockchain_identifier_from_name(self, name: str):
        url = f"{self.blockchain.value}/" \
              f"{self.network.value}/" \
              f"name_service/name_to_blockchain_identifier"
        response = self._request(
            endpoint=url,
            payload={
                'name': name
            },
            request_method=self._RequestMethod.POST
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response['blockchain_identifier']

    # -------------------------------------------------------------------------------------------- END: NAME SERVICE

    # -------------------------------------------------------------------------------------------- BEGIN: TOKENS

    def get_all_tokens(self):
        url = f"{self.blockchain.value}/" \
              f"{self.network.value}/" \
              f"all_tokens"
        response = self._request(
            endpoint=url,
            request_method=self._RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    def get_token_metadata(self, token_blockchain_identifier: str):
        url = f"{self.blockchain.value}/" \
              f"{self.network.value}/" \
              f"token/" \
              f"{token_blockchain_identifier}"
        response = self._request(
            endpoint=url,
            request_method=self._RequestMethod.GET
        )
        if 'error_message' in response:
            raise Exception(response['error_message'])
        return response

    # -------------------------------------------------------------------------------------------- END: WALLET
