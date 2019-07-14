class P2PConfiguration:
    def __init__(
        self,
        # TODO: is there better way of specifying these defaults? so some defaults can use others in their calculation?
        network: bytes = bytes.fromhex("feedbeef"),  # Mainnet constant TODO: move to a proper constants file
        node_id: int = 0,
        node_name: str = "FNode0",

        peer_request_interval: int = 60 * 3,  # 3 minutes
        peer_reseed_interval: int = 3600 * 4,  # 4 hours
        peer_ip_limit_incoming: int = 0,
        peer_ip_limit_outgoing: int = 0,
        special_peers: str = "",
        manual_ban: int = 3600 * 24 * 7,  # 1 week
        auto_ban: int = 3600 * 24 * 7,  # 1 week

        persist_file: str = "",
        persist_interval: int = 60 * 15,  # 15 minutes

        outgoing: int = 32,
        incoming: int = 150,
        fanout: int = 8,
        seed_url: str = None,
        peer_share_amount: int = 4 * 32,  # legacy math (4 * outgoing)
        minimum_quality_score: int = 20,
        persist_level: int = 2,
        persist_minimum: int = 60,  # 1 minute

        bind_ip: str = "",  # bind to all
        listen_port: str = "8108",
        listen_limit: int = 1,
        ping_interval: int = 15,  # 15 seconds
        persist_age_limit: int = 3600 * 48,  # 2 days
        redial_interval: int = 20,  # 20 seconds
        redial_reset: int = 3600 * 12,  # 12 hours
        redial_attempts: int = 5,
        disconnect_lock: int = 20 * 5 + 80,  # RedialInterval * RedialAttempts + 80 seconds

        read_deadline: int = 60 * 5,  # 5 minutes, high enough to accommodate large packets but fail eventually
        write_deadline: int = 60 * 5,  # 5 minutes, high enough to accommodate large packets but fail eventually
        handshake_timeout: int = 10,  # 10 seconds, can be quite low
        dial_timeout: int = 10,  # 10 seconds, can be quite low

        duplicate_filter: int = 3600,  # 1 hour
        duplicate_filter_cleanup: int = 60,  # 1 minute

        protocol_version: int = 10,
        protocol_version_minimum: int = 9,

        channel_capacity: int = 5000,
    ):
        """
        Defines the behavior of the gossip network protocol
        :param network: the NetworkID of the network to use, eg. MainNet, TestNet, etc
        :param node_id:
        :param node_name: the internal name of the node
        :param peer_request_interval: how often neighbors should be asked for an updated peer list
        :param peer_reseed_interval: how often the seed file should be accessed to check for changes
        :param peer_ip_limit_incoming: the maximum amount of peers to accept from a single ip address (0 for unlimited)
        :param peer_ip_limit_outgoing: the maximum amount of peers to accept from a single ip address (0 for unlimited)
        :param special_peers: a list of special peers, comma separated. If no port specified, the entire ip is special
        :param manual_ban: the duration to ban an address for when banned manually
        :param auto_ban: the duration to ban an address for when their quality score drops too low
        :param persist_file: the filepath to the file to save peers
        :param persist_interval: how often to save peers
        :param outgoing: the number of peers this node attempts to connect to
        :param incoming: the number of incoming connections this node is willing to accept
        :param fanout: controls how many random peers are selected for propagating messages
                       (higher values increase fault tolerance but also increase network congestion)
        :param seed_url: the URL of the remote seed file
        :param peer_share_amount: the number of peers we share (to count as being connected)
        :param minimum_quality_score:
        :param persist_level: 0 = persist all peers, 1 = persist peers we have had a connection with, or 2 persist only
                              peers we have been able to dial to
        :param persist_minimum: the minimum amount of time a connection has to last to last
        :param bind_ip: the ip address to bind to for listening and connecting (leave blank to bind to all)
        :param listen_port: the port to listen to incoming tcp connections on
        :param listen_limit: the lockout period of accepting connections from a single ip after having a successful
                             connection from that ip
        :param ping_interval: the maximum amount of time a connection can be silent (no writes) before sending a Ping
        :param persist_age_limit: how long a peer can be offline before being considered dead
        :param redial_interval: how long to wait between connection attempts
        :param redial_reset: after how long we should try to reconnect again
        :param redial_attempts: the number of redial attempts to make before considering a connection unreachable
        :param disconnect_lock: how long the peer manager should wait for an incoming peer to reconnect before
                                considering dialing to them
        :param read_deadline: the maximum time to read a single parcel. if a connection takes longer, it's disconnected
        :param write_deadline: the maximum time to send a single parcel. if a connection takes longer, it's disconnected
        :param handshake_timeout: the maximum time for an incoming connection to send the first parcel after connecting
        :param dial_timeout:
        :param duplicate_filter: how long message hashes are cashed to filter out duplicates (0 to disable)
        :param duplicate_filter_cleanup: how frequently the cleanup mechanism is run to trim duplicate filter memory
        :param protocol_version: the earliest version this package supports
        :param protocol_version_minimum:
        :param channel_capacity:
        """
        self.network = network
        self.node_id = node_id
        self.node_name = node_name

        # === Peer Management Settings ===
        self.peer_request_interval = peer_request_interval
        self.peer_reseed_interval = peer_reseed_interval
        self.peer_ip_limit_outgoing = peer_ip_limit_outgoing
        self.peer_ip_limit_incoming = peer_ip_limit_incoming

        self.special_peers = special_peers

        self.persist_file = persist_file
        self.persist_interval = persist_interval
        self.persist_level = persist_level
        self.persist_minimum = persist_minimum
        self.persist_age_limit = persist_age_limit

        self.peer_share_amount = peer_share_amount
        self.minimum_quality_score = minimum_quality_score

        # === Gossip Behavior ===
        self.outgoing = outgoing
        self.incoming = incoming
        self.fanout = fanout
        self.seed_url = seed_url

        # === Connection Settings ===
        self.bind_ip = bind_ip
        self.listen_port = listen_port
        self.listen_limit = listen_limit

        self.ping_interval = ping_interval
        self.redial_interval = redial_interval
        self.redial_reset = redial_reset
        self.redial_attempts = redial_attempts
        self.disconnect_lock = disconnect_lock

        self.manual_ban = manual_ban
        self.auto_ban = auto_ban

        self.handshake_timeout = handshake_timeout
        self.dial_timeout = dial_timeout
        self.read_deadline = read_deadline
        self.write_deadline = write_deadline

        self.duplicate_filter = duplicate_filter
        self.duplicate_filter_cleanup = duplicate_filter_cleanup

        self.protocol_version = protocol_version
        self.protocol_version_minimum = protocol_version_minimum

        self.channel_capacity = channel_capacity
