<template>
  <div class="event">
    <h1>This is an event page</h1>
    <router-link :to="{ name: 'CreateUpdateEvent', query: { id: this.$route.query.id}}">
      edit
    </router-link>
    <p>{{this.$route.query.id}}</p>
    <p>イベントID：{{ events.id }}</p>
    <p>タイトル：{{ events.title }}</p>
    <p>イベント紹介：{{ events.description }}</p>
    <p>主催者ID：{{ events.organizer }}</p>
    <p>主催者名：{{ events.organizer_first_name }}</p>
    <p>主催者アイコン：{{ events.organizer_icon }}</p>
    <p>イベントイメージ：{{ events.image }}</p>
    <p>イベント時間：{{ events.event_time }}</p>
    <p>イベント場所：{{ events.address }}</p>
    <p>料金：{{ events.fee }}</p>
    <p>ステータス：{{ events.status }}</p>
    <p>更新時間：{{ events.brief_updated_at }}</p>
    <BaseEvent v-on:parentGetEvent="getUser"></BaseEvent>
    <ParticipantList />
    <EventCommentList />
  </div>
</template>

<script>
import BaseEvent from '@/components/Event/BaseEvent.vue'
import ParticipantList from '@/components/Participant/ParticipantList.vue'
import EventCommentList from '@/components/EventComment/EventCommentList.vue'

export default {
  name: 'Event',
  data() {
    return {
      events: []
    }
  },
  components: {
    BaseEvent,
    ParticipantList,
    EventCommentList
  },
  methods: {
    getEvent: function(events) {
      this.events = events;
    }
  }
}
</script>
