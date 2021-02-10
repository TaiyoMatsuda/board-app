<template>
    <p>email：{{ event.email }}</p>
</template>
<script>
export default {
  name: 'UserEmail',
  data() {
    return {
      email: []
    }
  },
  mounted :function(){
    this.axios
      .get('api/users/' + this.$route.query.id + '/email/')
      .then(response => {this.email = response.data})
      .catch(error => console.log(error))
  }
}
</script>
