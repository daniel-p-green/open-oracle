"""Print a strict, temporary forwarding plan. Never connects or changes SSH state."""
import argparse
import ipaddress
import json
import re
import shlex


def reverse_forward(host, user, *, app_port=8765, pi_port=8765):
    try:
        ip = ipaddress.ip_address(host)
    except ValueError as error:
        raise ValueError('Use the freshly verified Pi IPv4 address') from error
    if ip.version != 4 or not ip.is_private or ip.is_loopback or ip.is_unspecified or ip.is_multicast or ip.is_link_local:
        raise ValueError('Expected the verified private Pi IPv4 address')
    if not isinstance(user, str) or not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}', user):
        raise ValueError('Invalid verified Pi account name')
    if any(type(p) is not int or not 1024 <= p <= 65535 for p in (app_port, pi_port)):
        raise ValueError('Use unprivileged valid ports')
    return ['ssh', '-N', '-T', '-o', 'ExitOnForwardFailure=yes', '-o', 'StrictHostKeyChecking=yes',
            '-o', 'ForwardAgent=no', '-o', 'ForwardX11=no', '-o', 'ControlMaster=no', '-o', 'ControlPath=none',
            '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=2',
            '-R', f'127.0.0.1:{pi_port}:127.0.0.1:{app_port}', f'{user}@{ip}']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pi-host', required=True)
    parser.add_argument('--pi-user', required=True)
    parser.add_argument('--app-port', type=int, default=8765)
    parser.add_argument('--pi-port', type=int, default=8765)
    args = parser.parse_args()
    argv = reverse_forward(args.pi_host, args.pi_user, app_port=args.app_port, pi_port=args.pi_port)
    print(json.dumps({'execute': False, 'argv': argv, 'command': shlex.join(argv),
                      'pi_url': f'http://127.0.0.1:{args.pi_port}/',
                      'requires': ['fresh Pi identity and fingerprint verification', 'explicit temporary forwarding approval',
                                   'existing verified SSH login or direct human authentication', 'free Pi loopback port',
                                   'actual loopback/secure-context verification before device tests']}, indent=2))


if __name__ == '__main__':
    main()
