from django.shortcuts import render

from django.contrib.auth import get_user_model
from .models import (
    ChatSession, ChatSessionMember, ChatSessionMessage, deserialize_user
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from notifications.signals import notify

class ChatSessionView(APIView):


    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        
        user = request.user
        print(request.user)
        chat_session = ChatSession.objects.create(owner=user)

        return Response({
            'status': 'SUCCESS', 'uri': chat_session.uri,
            'message': 'New chat session created'
        })

    def patch(self, request, *args, **kwargs):
   
        User = get_user_model()

        uri = kwargs['uri']
        username = request.data['username']
        user = User.objects.get(username=username)

        chat_session = ChatSession.objects.get(uri=uri)
        owner = chat_session.owner

        if owner != user: 
            newMember = chat_session.members.get_or_create(
                user=user, chat_session=chat_session
            )
            notif_args = {
                'source': user,
                'source_display_name': user.get_full_name(),
                'category': 'chat', 'action': 'Sent',
                'obj': newMember[0].id,
                'short_description': 'You a new member', 'silent': True,
                'extra_data': {
                    'uri': chat_session.uri,
                    'member': newMember[0].to_json()
                }
            }
            print(newMember[0].to_json())
            notify.send(
              sender=self.__class__,**notif_args, channels=['member']
            ) 
        owner = deserialize_user(owner)
        members = [
                deserialize_user(chat_session.user) 
                for chat_session in chat_session.members.all()
            ]
        
        members.insert(0, owner) 

        return Response ({
            'status': 'SUCCESS', 'members': members,
            'message': '%s joined that chat' % user.username,
            'user': deserialize_user(user)
        })

    def get(self, request, *args, **kwargs):
            uri = kwargs['uri']
            chat_session = ChatSession.objects.get(uri=uri)

            owner = deserialize_user(chat_session.owner)
            members = [
                    deserialize_user(chat_session.user) 
                    for chat_session in chat_session.members.all()
                ]
            members.insert(0, owner)
            return Response ({
            'status': 'SUCCESS', 'members': members
        }) 

    

class ChatSessionMessageView(APIView):
  

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
    
        uri = kwargs['uri']
       
        chat_session = ChatSession.objects.get(uri=uri)
        messages = [chat_session_message.to_json() 
            for chat_session_message in chat_session.messages.all()]
        
        return Response({
            'id': chat_session.id, 'uri': chat_session.uri,
            'messages': messages
        })

    def post(self, request, *args, **kwargs):
        """create a new message in a chat session."""
        uri = kwargs['uri']
        message = request.data['message']

        user = request.user
        chat_session = ChatSession.objects.get(uri=uri)

        chat_session_message = ChatSessionMessage.objects.create(
            user=user, chat_session=chat_session, message=message
        )

        notif_args = {
            'source': user,
            'source_display_name': user.get_full_name(),
            'category': 'chat', 'action': 'Sent',
            'obj': chat_session_message.id,
            'short_description': 'You a new message', 'silent': True,
            'extra_data': {
                'uri': chat_session.uri,
                'message': chat_session_message.to_json()
            }
        }
        notify.send(
            sender=self.__class__,**notif_args, channels=['websocket']
        )

        return Response ({
            'status': 'SUCCESS', 'uri': chat_session.uri, 'message': message,
            'user': deserialize_user(user)
        })

    def patch(self, request, *args, **kwargs):
        
        User = get_user_model()

        uri = kwargs['uri']
        message_id = request.data['message']['id']
        message = request.data['message']
        
        username = request.data['username']
        user = User.objects.get(username=username)

        chat_session = ChatSession.objects.get(uri=uri)
        chat_session_message = chat_session.messages.get(pk=message_id)

        if chat_session_message.user != user:
            reader=chat_session_message.readers.get_or_create(
                user=user, isRead=chat_session_message, 
            )
            # notif_args = {
            #     'source': user,
            #     'source_display_name': user.get_full_name(),
            #     'category': 'chat', 'action': 'Sent',
            #     'obj': reader[0].id,
            #     'short_description': 'You a new member', 'silent': True,
            #     'extra_data': {
            #         'uri': chat_session.uri,
            #         'member': reader[0].to_json()
            #     }
            # }
            #sprint(deserialize_user(reader[0]))
            # notify.send(
            #   sender=self.__class__,**notif_args, channels=['member']
            # ) 
        readers = [deserialize_user(reader.user) 
            for reader in chat_session_message.readers.all()]            

        return Response ({
            'status': 'SUCCESS',
            'message': '%s reading message' % reader[0].user.username,
            'readers':readers
        })        


