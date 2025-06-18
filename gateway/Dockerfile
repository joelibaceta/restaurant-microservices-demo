FROM nginx:1.25

# Instalar consul-template
RUN apt-get update && \
    apt-get install -y unzip curl && \
    curl -sSL https://releases.hashicorp.com/consul-template/0.33.0/consul-template_0.33.0_linux_amd64.zip -o ct.zip && \
    unzip ct.zip && mv consul-template /usr/local/bin/ && rm ct.zip

COPY nginx.ctmpl /etc/consul-template/nginx.ctmpl
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]