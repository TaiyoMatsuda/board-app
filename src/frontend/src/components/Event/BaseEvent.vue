<template>
  <div>
    <p>{{this.$route.query.id}}</p>
    <p>{{ events }}</p>
  </div>
</template>

<script>
export default {
  name: 'BaseEvent',
  data() {
    return {
      events: []
    };
  },
  mounted :function(){
    console.log('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
    this.axios
      .get('https://jsonplaceholder.typicode.com/users/' + this.$route.query.id)
      .then(response => {this.events = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
