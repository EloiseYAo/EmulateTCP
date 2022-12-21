// Fill in your client ID and client secret that you obtained
// while registering the application
const clientID = '5b8837fe0d2ccb36fb64'
const clientSecret = 'bc4cf18960135ceab41ca5fb7401cd2b115915d4'

const Koa = require('koa');
const path = require('path');
const serve = require('koa-static');
const route = require('koa-route');
const axios = require('axios');

const app = new Koa();

const main = serve(path.join(__dirname));

const oauth = async ctx => {
    const requestToken = ctx.request.query.code;
    console.log('authorization code:', requestToken);

    const tokenResponse = await axios({
        method: 'post',
        url: 'https://github.com/login/oauth/access_token?' +
            `client_id=${clientID}&` +
            `client_secret=${clientSecret}&` +
            `code=${requestToken}`,
        headers: {
            accept: 'application/json'
        }
    });

    const accessToken = tokenResponse.data.access_token;
    console.log(`access token: ${accessToken}`);

    const result = await axios({
        method: 'get',
        url: `https://api.github.com/user`,
        headers: {
            accept: 'application/json',
            Authorization: `token ${accessToken}`
        }
    });
    console.log(result.data);
    const name = result.data.name;

    ctx.response.redirect(`/home.html`);
};

app.use(main);
app.use(route.get('/oauth/redirect', oauth));

app.listen(8080);