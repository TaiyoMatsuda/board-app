<template>
  <div id="app">
    <div id="nav">
      <router-link to="/">Home</router-link>|
      <router-link :to="{ name: 'User', query: { id: 3}}">profile</router-link>|
      <a v-on:click="show" class="modal_open">login</a>|
      <router-link to="/logout">logout</router-link>|
      <modal name="login" :draggable="true" :resizable="true">
        <Login />
      </modal>
    </div>
    <router-view/>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

.modal_open {
  cursor: pointer;
}

.modal-header, .modal-body {
  padding: 5px 25px;
}
.modal-header {
  border-bottom: 1px solid #ddd;
}
</style>

<script>
import Login from '@/views/Login.vue'
export default {
  components: {
    Login
  },
  methods: {
    show : function() {
      this.$modal.show('login');
    },
    hide : function () {
      this.$modal.hide('login');
    },
  }
}
</script>
