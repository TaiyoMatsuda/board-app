<template>
  <div>
    <p>Event List</p>
    <div v-for="(event, key) in events" :key="key">
      <hr>
        <p>{{ event.name }}</p>
        <router-link :to="{ name: 'Event', query: { id: event.id}}">
          more
        </router-link>
      <hr>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EventList',
  data() {
    return {
      events: []
    };
  },
  mounted :function(){
    this.axios
      .get('https://jsonplaceholder.typicode.com/users')
      .then(response => {this.events = response.data})
      .catch(error => console.log(error))
  }
}
</script>


<style scoped>
</style>
