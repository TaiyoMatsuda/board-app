<template>
  <div id="login" class="login">
    <h1>This is a login page</h1>
      <div class="form-group">
          <label>Email</label>
          <input type="email" class="form-control" placeholder="Emailを入力してください" v-model="email">
      </div>
      <div class="form-group">
          <label>Password</label>
          <input type="password" class="form-control" placeholder="passwordを入力してください" v-model="password">
      </div>
      <button class="btn btn-primary">login</button>
      <br />
      <a>Create</a>
  </div>
</template>

<script>
export default {
  name: 'Login',
  form:{
    email:'',
    password:''
  },
  users: [],
}
</script>
