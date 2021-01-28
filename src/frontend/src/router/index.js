import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import User from '../views/User.vue'
import UpdateUser from '../views/UpdateUser.vue'
import Event from '../views/Event.vue'
import CreateUpdateEvent from '../views/CreateUpdateEvent.vue'
import Login from '../views/Login.vue'
import Logout from '../views/Logout.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/user',
    name: 'User',
    component: User
  },
  {
    path: '/update_user',
    name: 'UpdateUser',
    component: UpdateUser
  },
  {
    path: '/update_password',
    name: 'UpdatePassword',
    component: () => import(/* webpackChunkName: "create event" */ '../views/UpdatePassword.vue')
  },
  {
    path: '/create_update_event',
    name: 'CreateUpdateEvent',
    component: CreateUpdateEvent
  },
  {
    path: '/event',
    name: 'Event',
    component: Event
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/logout',
    name: 'Logout',
    component: Logout
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
