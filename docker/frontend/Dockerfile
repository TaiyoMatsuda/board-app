FROM node:14.14.0

WORKDIR /code

RUN npm install

ADD ./src/frontend/ /code/

CMD ["npm", "run", "serve"]