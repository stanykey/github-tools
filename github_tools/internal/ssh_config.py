"""Simple SSH config reader."""
from dataclasses import dataclass
from dataclasses import field
from enum import auto
from enum import Enum
from os import PathLike
from typing import TextIO


class SshConfigError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class SshKeyword(Enum):
    """Values were taken from **`man ssh`**."""

    AddressFamily = auto()
    BatchMode = auto()
    BindAddress = auto()
    ChallengeResponseAuthentication = auto()
    CheckHostIP = auto()
    Cipher = auto()
    Ciphers = auto()
    ClearAllForwardings = auto()
    Compression = auto()
    CompressionLevel = auto()
    ConnectionAttempts = auto()
    ConnectTimeout = auto()
    ControlMaster = auto()
    ControlPath = auto()
    DynamicForward = auto()
    EscapeChar = auto()
    ExitOnForwardFailure = auto()
    ForwardAgent = auto()
    ForwardX11 = auto()
    ForwardX11Trusted = auto()
    GatewayPorts = auto()
    GlobalKnownHostsFile = auto()
    GSSAPIAuthentication = auto()
    GSSAPIDelegateCredentials = auto()
    HashKnownHosts = auto()
    Host = auto()
    HostbasedAuthentication = auto()
    HostKeyAlgorithms = auto()
    HostKeyAlias = auto()
    HostName = auto()
    IdentityFile = auto()
    IdentitiesOnly = auto()
    KbdInteractiveDevices = auto()
    LocalCommand = auto()
    LocalForward = auto()
    LogLevel = auto()
    MACs = auto()
    NoHostAuthenticationForLocalhost = auto()
    NumberOfPasswordPrompts = auto()
    PasswordAuthentication = auto()
    PermitLocalCommand = auto()
    Port = auto()
    PreferredAuthentications = auto()
    Protocol = auto()
    ProxyCommand = auto()
    PubkeyAuthentication = auto()
    RekeyLimit = auto()
    RemoteForward = auto()
    RhostsRSAAuthentication = auto()
    RSAAuthentication = auto()
    SendEnv = auto()
    ServerAliveInterval = auto()
    ServerAliveCountMax = auto()
    SmartcardDevice = auto()
    StrictHostKeyChecking = auto()
    TCPKeepAlive = auto()
    Tunnel = auto()
    TunnelDevice = auto()
    UsePrivilegedPort = auto()
    User = auto()
    UserKnownHostsFile = auto()
    VerifyHostKeyDNS = auto()
    VisualHostKey = auto()
    XAuthLocation = auto()


HostInfo = dict[SshKeyword, str]


@dataclass
class HostConfig:
    host: str
    params: HostInfo = field(default_factory=dict)


class SshConfig:
    def __init__(self, file: TextIO) -> None:
        self._hosts: dict[str, HostInfo] = {config.host: config.params for config in self._load(file)}

    @property
    def hosts(self) -> list[str]:
        """Return list of hosts."""
        return list(self._hosts.keys())

    def get(self, host: str) -> HostInfo | None:
        """Get the `host` config is present otherwise **None**."""
        return self._hosts.get(host)

    def __contains__(self, host: str) -> bool:
        """Check for config for the `host`."""
        return host in self._hosts

    def is_valid(self) -> bool:
        """Check the correctness of the config."""
        if not self._hosts:
            return True  # empty config is ok

        return all(self._hosts.keys())

    @classmethod
    def verify_file(cls, path: str | PathLike[str]) -> bool:
        """
        Verify the validity of SSH configuration.

        The current implementation is pretty weak but this is better than nothing.
        Maybe it's much better to call ```ssh -T -F path```
        """
        try:
            with open(path, encoding="utf-8") as file:
                return cls(file).is_valid()
        except SshConfigError:
            return False

    @classmethod
    def _load(cls, file: TextIO) -> list[HostConfig]:
        hosts: list[HostConfig] = []

        # empty lines and lines starting with '#' are comments.
        filter_comments = (line.strip() for line in file if not line.startswith("#") and line.strip())
        parser = (cls._parse(line) for line in filter_comments)
        for option, value in parser:
            match option:
                case SshKeyword.Host:
                    hosts.append(HostConfig(value))
                case _:
                    hosts[-1].params[option] = value

        return hosts

    @staticmethod
    def _parse(line: str) -> tuple[SshKeyword, str]:
        """
        Parse ssh config line.

        Rules:
            - each line begins with a keyword, followed by argument(s).
            - configuration options may be separated by whitespace or optional whitespace and exactly one =.
            - arguments may be enclosed in double quotes (") in order to specify arguments that contain spaces.
        """
        option, separator, value = line.partition(" ")
        try:
            return SshKeyword[option], value.strip('=" ')
        except KeyError:
            raise SshConfigError("ssh config contains unknown keyword")
