FROM ubuntu:20.04
RUN apt update && apt upgrade -y
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt install apache2 -y
RUN apt install -y php7.4 php7.4-cli php7.4-json php7.4-common php7.4-mysql php7.4-zip php7.4-gd php7.4-mbstring php7.4-curl php7.4-xml php7.4-bcmath
COPY src/ /var/www/html/ 
COPY flag.txt /
RUN chmod 777 /flag.txt
RUN mkdir /var/www/html/tmp && chmod 777 /var/www/html/tmp
RUN service apache2 restart
CMD ["apache2ctl", "-D", "FOREGROUND"]