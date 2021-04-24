import Vue from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import VModal from 'vue-js-modal'

axios.defaults.baseURL = 'http://127.0.0.1:8000/'
axios.defaults.headers.common['Accept'] = 'application/json'
axios.defaults.headers.common['Content-Type'] = 'application/json;charset=utf-8'
axios.defaults.headers.common['Access-Control-Allow-Origin'] = 'http://127.0.0.1:8080/'
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

Vue.config.productionTip = false

export { axios };
Vue.use(VModal);

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
