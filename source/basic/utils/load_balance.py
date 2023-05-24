import hashlib
import random
from abc import ABC, abstractmethod
from typing import Union, List

from fastapi import Request

from services.auth.util.settings import settings


class LoadBalancerBase(ABC):
    def __init__(self, servers: List):
        self.servers = servers

    @abstractmethod
    async def get_server(self, request: Union[Request, None] = None):
        pass


class RoundRobinLoadBalancer(LoadBalancerBase):
    def __init__(self, servers: List):
        super().__init__(servers)
        self.current = 0

    async def get_server(self, request: Union[Request, None] = None):
        if len(self.servers) == 1:
            return self.servers[0]
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        print(self.servers)
        return server


class IpHashLoadBalancer(LoadBalancerBase):
    def __init__(self, servers: List):
        super().__init__(servers)

    async def get_server(self, request: Union[Request, None] = None):
        if len(self.servers) == 1:
            return self.servers[0]
        index = int(hashlib.md5(request.client.host.encode()).hexdigest(), 16) % len(self.servers)
        return self.servers[index]


class RandomLoadBalancer(LoadBalancerBase):
    def __init__(self, servers: List):
        super().__init__(servers)

    async def get_server(self, request: Union[Request, None] = None):
        if len(self.servers) == 1:
            return self.servers[0]
        return random.choice(self.servers)


load_balancer_factory = {
    "round_robin": RoundRobinLoadBalancer,
    "ip_hash": IpHashLoadBalancer,
    "random": RandomLoadBalancer,
}

rule = load_balancer_factory.get(settings.LOAD_BALANCER_RULE, RoundRobinLoadBalancer)
api_key_server = rule(settings.OPENAI_API_KEY)
