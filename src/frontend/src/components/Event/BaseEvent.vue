<script>
export default {
  name: 'BaseEvent',
  mounted :function(){
    console.log('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
    this.axios
      .get('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
      .then(response => this.$emit('parentGetEvent', response.data))
      .catch(error => console.log(error))
  }
}
</script>