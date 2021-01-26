<template>
  <div>
    <p>{{this.$route.query.id}}</p>
    <p>{{ events.id }}</p>
    <p>{{ events.title }}</p>
    <p>{{ events.description }}</p>
    <p>{{ events.organizer }}</p>
    <p>{{ events.organizer_first_name }}</p>
    <p>{{ events.organizer_icon }}</p>
    <p>{{ events.image }}</p>
    <p>{{ events.event_time }}</p>
    <p>{{ events.address }}</p>
    <p>{{ events.fee }}</p>
    <p>{{ events.status }}</p>
    <p>{{ events.brief_updated_at }}</p>
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
