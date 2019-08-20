FROM alpine
RUN apk --no-cache add dnsmasq
RUN touch /tmp/dhcp.leases /tmp/resolv.conf.auto
RUN echo `whoami` && chown `whoami`:`whoami` /tmp/dhcp.leases /tmp/resolv.conf.auto
COPY ./dnsmasq.conf /etc/dnsmasq.conf
COPY ./hostname /etc/hostname
COPY ./hosts /etc/hosts
COPY ./resolv.conf /etc/resolv.conf

ENTRYPOINT ["dnsmasq", "-d"]
