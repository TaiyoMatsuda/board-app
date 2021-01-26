import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Event from '../views/Event.vue'
import User from '../views/User.vue'
import UpdateUser from '../views/UpdateUser.vue'

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
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "create event" */ '../views/CreateUpdateEvent.vue')
  },
  {
    path: '/event',
    name: 'Event',
    component: Event
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
