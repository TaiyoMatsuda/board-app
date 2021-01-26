<template>
  <div>
    <p>{{this.$route.query.id}}</p>
    <p>{{ user.id }}</p>
    <p>{{ user.username }}</p>
    <p>{{ user.email }}</p>
    <p>{{ user.first_name }}</p>
    <p>{{ user.email }}</p>
    <p>{{ user.email }}</p>
    <p>{{ user.email }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseUser',
  data() {
    return {
      user: []
    };
  },
  mounted :function(){
    console.log('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
    this.axios
      .get('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
      .then(response => {this.user = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
