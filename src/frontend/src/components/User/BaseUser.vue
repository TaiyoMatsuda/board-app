<script>
export default {
  name: 'BaseUser',
  mounted :function(){
    console.log('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
    this.axios
      .get('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
      .then(response => this.$emit('parentGetUser', response.data))
      .catch(error => console.log(error))
  }
}
</script>
