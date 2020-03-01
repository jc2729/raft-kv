# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rpc.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='rpc.proto',
  package='rpc',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\trpc.proto\x12\x03rpc\"\xbb\x07\n\x03Rpc\x12\x1b\n\x04type\x18\x01 \x02(\x0e\x32\r.rpc.Rpc.Type\x12%\n\x07voteReq\x18\x02 \x01(\x0b\x32\x14.rpc.Rpc.RequestVote\x12(\n\x07voteRes\x18\x03 \x01(\x0b\x32\x17.rpc.Rpc.RequestVoteRes\x12\x30\n\x10\x61ppendEntriesReq\x18\x04 \x01(\x0b\x32\x16.rpc.Rpc.AppendEntries\x12\x33\n\x10\x61ppendEntriesRes\x18\x05 \x01(\x0b\x32\x19.rpc.Rpc.AppendEntriesRes\x12/\n\x0chandshakeReq\x18\x06 \x01(\x0b\x32\x19.rpc.Rpc.RequestHandshake\x12\x32\n\x0chandshakeRes\x18\x07 \x01(\x0b\x32\x1c.rpc.Rpc.RequestHandshakeRes\x1a\x64\n\x0bRequestVote\x12\x15\n\rcandidateTerm\x18\x01 \x02(\x05\x12\x13\n\x0b\x63\x61ndidateId\x18\x02 \x02(\x05\x12\x14\n\x0clastLogIndex\x18\x03 \x02(\x05\x12\x13\n\x0blastLogTerm\x18\x04 \x02(\x05\x1aV\n\x0eRequestVoteRes\x12\x0c\n\x04term\x18\x01 \x02(\x05\x12\x13\n\x0bvoteGranted\x18\x02 \x02(\x08\x12\n\n\x02id\x18\x03 \x02(\x05\x12\x15\n\rcandidateTerm\x18\x04 \x02(\x05\x1a\x96\x01\n\rAppendEntries\x12\x12\n\nleaderTerm\x18\x01 \x02(\x05\x12\x10\n\x08leaderId\x18\x02 \x02(\x05\x12\x14\n\x0cprevLogIndex\x18\x03 \x02(\x05\x12\x13\n\x0bprevLogTerm\x18\x04 \x02(\x05\x12\x1e\n\x07\x65ntries\x18\x05 \x03(\x0b\x32\r.rpc.LogEntry\x12\x14\n\x0cleaderCommit\x18\x06 \x02(\x05\x1aQ\n\x10\x41ppendEntriesRes\x12\x0c\n\x04term\x18\x01 \x02(\x05\x12\x0f\n\x07success\x18\x02 \x02(\x08\x12\n\n\x02id\x18\x03 \x02(\x05\x12\x12\n\nleaderTerm\x18\x04 \x02(\x05\x1a\x1e\n\x10RequestHandshake\x12\n\n\x02id\x18\x01 \x02(\x05\x1a!\n\x13RequestHandshakeRes\x12\n\n\x02id\x18\x01 \x02(\x05\"\x8c\x01\n\x04Type\x12\x10\n\x0cREQUEST_VOTE\x10\x00\x12\x14\n\x10REQUEST_VOTE_RES\x10\x01\x12\x12\n\x0e\x41PPEND_ENTRIES\x10\x02\x12\x16\n\x12\x41PPEND_ENTRIES_RES\x10\x03\x12\x15\n\x11REQUEST_HANDSHAKE\x10\x04\x12\x19\n\x15REQUEST_HANDSHAKE_RES\x10\x05\")\n\x08LogEntry\x12\x0f\n\x07\x63ommand\x18\x01 \x02(\t\x12\x0c\n\x04term\x18\x02 \x02(\x05')
)



_RPC_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='rpc.Rpc.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='REQUEST_VOTE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUEST_VOTE_RES', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='APPEND_ENTRIES', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='APPEND_ENTRIES_RES', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUEST_HANDSHAKE', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REQUEST_HANDSHAKE_RES', index=5, number=5,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=834,
  serialized_end=974,
)
_sym_db.RegisterEnumDescriptor(_RPC_TYPE)


_RPC_REQUESTVOTE = _descriptor.Descriptor(
  name='RequestVote',
  full_name='rpc.Rpc.RequestVote',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='candidateTerm', full_name='rpc.Rpc.RequestVote.candidateTerm', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='candidateId', full_name='rpc.Rpc.RequestVote.candidateId', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lastLogIndex', full_name='rpc.Rpc.RequestVote.lastLogIndex', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='lastLogTerm', full_name='rpc.Rpc.RequestVote.lastLogTerm', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=340,
  serialized_end=440,
)

_RPC_REQUESTVOTERES = _descriptor.Descriptor(
  name='RequestVoteRes',
  full_name='rpc.Rpc.RequestVoteRes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='term', full_name='rpc.Rpc.RequestVoteRes.term', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='voteGranted', full_name='rpc.Rpc.RequestVoteRes.voteGranted', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='rpc.Rpc.RequestVoteRes.id', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='candidateTerm', full_name='rpc.Rpc.RequestVoteRes.candidateTerm', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=442,
  serialized_end=528,
)

_RPC_APPENDENTRIES = _descriptor.Descriptor(
  name='AppendEntries',
  full_name='rpc.Rpc.AppendEntries',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='leaderTerm', full_name='rpc.Rpc.AppendEntries.leaderTerm', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='leaderId', full_name='rpc.Rpc.AppendEntries.leaderId', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='prevLogIndex', full_name='rpc.Rpc.AppendEntries.prevLogIndex', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='prevLogTerm', full_name='rpc.Rpc.AppendEntries.prevLogTerm', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='entries', full_name='rpc.Rpc.AppendEntries.entries', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='leaderCommit', full_name='rpc.Rpc.AppendEntries.leaderCommit', index=5,
      number=6, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=531,
  serialized_end=681,
)

_RPC_APPENDENTRIESRES = _descriptor.Descriptor(
  name='AppendEntriesRes',
  full_name='rpc.Rpc.AppendEntriesRes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='term', full_name='rpc.Rpc.AppendEntriesRes.term', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='success', full_name='rpc.Rpc.AppendEntriesRes.success', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='rpc.Rpc.AppendEntriesRes.id', index=2,
      number=3, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='leaderTerm', full_name='rpc.Rpc.AppendEntriesRes.leaderTerm', index=3,
      number=4, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=683,
  serialized_end=764,
)

_RPC_REQUESTHANDSHAKE = _descriptor.Descriptor(
  name='RequestHandshake',
  full_name='rpc.Rpc.RequestHandshake',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='rpc.Rpc.RequestHandshake.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=766,
  serialized_end=796,
)

_RPC_REQUESTHANDSHAKERES = _descriptor.Descriptor(
  name='RequestHandshakeRes',
  full_name='rpc.Rpc.RequestHandshakeRes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='rpc.Rpc.RequestHandshakeRes.id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=798,
  serialized_end=831,
)

_RPC = _descriptor.Descriptor(
  name='Rpc',
  full_name='rpc.Rpc',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='rpc.Rpc.type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='voteReq', full_name='rpc.Rpc.voteReq', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='voteRes', full_name='rpc.Rpc.voteRes', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='appendEntriesReq', full_name='rpc.Rpc.appendEntriesReq', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='appendEntriesRes', full_name='rpc.Rpc.appendEntriesRes', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='handshakeReq', full_name='rpc.Rpc.handshakeReq', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='handshakeRes', full_name='rpc.Rpc.handshakeRes', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_RPC_REQUESTVOTE, _RPC_REQUESTVOTERES, _RPC_APPENDENTRIES, _RPC_APPENDENTRIESRES, _RPC_REQUESTHANDSHAKE, _RPC_REQUESTHANDSHAKERES, ],
  enum_types=[
    _RPC_TYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=19,
  serialized_end=974,
)


_LOGENTRY = _descriptor.Descriptor(
  name='LogEntry',
  full_name='rpc.LogEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='command', full_name='rpc.LogEntry.command', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='term', full_name='rpc.LogEntry.term', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=976,
  serialized_end=1017,
)

_RPC_REQUESTVOTE.containing_type = _RPC
_RPC_REQUESTVOTERES.containing_type = _RPC
_RPC_APPENDENTRIES.fields_by_name['entries'].message_type = _LOGENTRY
_RPC_APPENDENTRIES.containing_type = _RPC
_RPC_APPENDENTRIESRES.containing_type = _RPC
_RPC_REQUESTHANDSHAKE.containing_type = _RPC
_RPC_REQUESTHANDSHAKERES.containing_type = _RPC
_RPC.fields_by_name['type'].enum_type = _RPC_TYPE
_RPC.fields_by_name['voteReq'].message_type = _RPC_REQUESTVOTE
_RPC.fields_by_name['voteRes'].message_type = _RPC_REQUESTVOTERES
_RPC.fields_by_name['appendEntriesReq'].message_type = _RPC_APPENDENTRIES
_RPC.fields_by_name['appendEntriesRes'].message_type = _RPC_APPENDENTRIESRES
_RPC.fields_by_name['handshakeReq'].message_type = _RPC_REQUESTHANDSHAKE
_RPC.fields_by_name['handshakeRes'].message_type = _RPC_REQUESTHANDSHAKERES
_RPC_TYPE.containing_type = _RPC
DESCRIPTOR.message_types_by_name['Rpc'] = _RPC
DESCRIPTOR.message_types_by_name['LogEntry'] = _LOGENTRY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Rpc = _reflection.GeneratedProtocolMessageType('Rpc', (_message.Message,), {

  'RequestVote' : _reflection.GeneratedProtocolMessageType('RequestVote', (_message.Message,), {
    'DESCRIPTOR' : _RPC_REQUESTVOTE,
    '__module__' : 'rpc_pb2'
    # @@protoc_insertion_point(class_scope:rpc.Rpc.RequestVote)
    })
  ,

  'RequestVoteRes' : _reflection.GeneratedProtocolMessageType('RequestVoteRes', (_message.Message,), {
    'DESCRIPTOR' : _RPC_REQUESTVOTERES,
    '__module__' : 'rpc_pb2'
    # @@protoc_insertion_point(class_scope:rpc.Rpc.RequestVoteRes)
    })
  ,

  'AppendEntries' : _reflection.GeneratedProtocolMessageType('AppendEntries', (_message.Message,), {
    'DESCRIPTOR' : _RPC_APPENDENTRIES,
    '__module__' : 'rpc_pb2'
    # @@protoc_insertion_point(class_scope:rpc.Rpc.AppendEntries)
    })
  ,

  'AppendEntriesRes' : _reflection.GeneratedProtocolMessageType('AppendEntriesRes', (_message.Message,), {
    'DESCRIPTOR' : _RPC_APPENDENTRIESRES,
    '__module__' : 'rpc_pb2'
    # @@protoc_insertion_point(class_scope:rpc.Rpc.AppendEntriesRes)
    })
  ,

  'RequestHandshake' : _reflection.GeneratedProtocolMessageType('RequestHandshake', (_message.Message,), {
    'DESCRIPTOR' : _RPC_REQUESTHANDSHAKE,
    '__module__' : 'rpc_pb2'
    # @@protoc_insertion_point(class_scope:rpc.Rpc.RequestHandshake)
    })
  ,

  'RequestHandshakeRes' : _reflection.GeneratedProtocolMessageType('RequestHandshakeRes', (_message.Message,), {
    'DESCRIPTOR' : _RPC_REQUESTHANDSHAKERES,
    '__module__' : 'rpc_pb2'
    # @@protoc_insertion_point(class_scope:rpc.Rpc.RequestHandshakeRes)
    })
  ,
  'DESCRIPTOR' : _RPC,
  '__module__' : 'rpc_pb2'
  # @@protoc_insertion_point(class_scope:rpc.Rpc)
  })
_sym_db.RegisterMessage(Rpc)
_sym_db.RegisterMessage(Rpc.RequestVote)
_sym_db.RegisterMessage(Rpc.RequestVoteRes)
_sym_db.RegisterMessage(Rpc.AppendEntries)
_sym_db.RegisterMessage(Rpc.AppendEntriesRes)
_sym_db.RegisterMessage(Rpc.RequestHandshake)
_sym_db.RegisterMessage(Rpc.RequestHandshakeRes)

LogEntry = _reflection.GeneratedProtocolMessageType('LogEntry', (_message.Message,), {
  'DESCRIPTOR' : _LOGENTRY,
  '__module__' : 'rpc_pb2'
  # @@protoc_insertion_point(class_scope:rpc.LogEntry)
  })
_sym_db.RegisterMessage(LogEntry)


# @@protoc_insertion_point(module_scope)
