from __future__ import absolute_import
# -*- coding: utf-8 -*-
import base64
import six

__author__ = 'freekoder'

from .comment import Comment
from .remote_obj import RemoteObject
from .subtask import Subtask
from .attachment import Attachment

# TODO: create aliases for update


class Task(RemoteObject):

    OPENED = 1
    CLOSED = 0

    COLOR_YELLOW = 'yellow'
    COLOR_BLUE = 'blue'
    COLOR_RED = 'red'
    COLOR_GREEN = 'green'
    COLOR_PURPLE = 'purple'
    COLOR_ORANGE = 'orange'
    COLOR_GRAY = 'gray'

    def __init__(self, project, props):
        self.project = project
        self.id = int(props['id'])
        self.title = props['title']
        self.description = props['description']
        self.date_creation = props['date_creation']
        self.color = props['color_id']
        self.column = project.get_column_by_id(int(props['column_id']))
        self.owner = project.board.get_user_by_id(int(props['owner_id']))
        self.position = int(props['position'])
        self.is_active = True if props['is_active'] == '1' else False
        self.date_completed = props['date_completed']
        self.score = props['score']
        self.date_due = props['date_due']
        self.category = project.get_category_by_id(int(props['category_id']))
        self.creator = project.board.get_user_by_id(int(props['creator_id']))
        self.date_modification = props['date_modification']
        self.swimlane = project.get_swimlane_by_id(int(props['swimlane_id']))
        self.date_completed = props['date_completed']
        self.reference = props['reference']
        self.date_modification = props['date_modification']
        self.date_started = props['date_started']
        self.time_spent = props['time_spent']
        self.time_estimated = props['time_estimated']
        self.date_moved = props['date_moved']
        self.recurrence_status = props['recurrence_status'] if 'recurrence_status' in props else None
        self.recurrence_trigger = props['recurrence_trigger'] if 'recurrence_trigger' in props else None
        self.recurrence_factor = props['recurrence_factor'] if 'recurrence_factor' in props else None
        self.recurrence_timeframe = props['recurrence_timeframe'] if 'recurrence_timeframe' in props else None
        self.recurrence_basedate = props['recurrence_basedate'] if 'recurrence_basedate' in props else None
        self.recurrence_parent = props['recurrence_parent'] if 'recurrence_parent' in props else None
        self.recurrence_child = props['recurrence_child'] if 'recurrence_child' in props else None

        super(Task, self).__init__(project.url, project.token)

    # TODO: implement recurrence fields
    # TODO: category, owner or swimlane could be None
    def update(self, title=None, color=None, column=None,
               description=None, owner=None, creator=None,
               score=None, date_due=None, category=None, swimlane=None):
        props = {'id': self.id, 'project_id': self.project.id}
        if title:
            props['title'] = title
        if color:
            props['color_id'] = color
        if column:
            props['column_id'] = column.id
        if description:
            props['description'] = description
        if owner:
            props['owner_id'] = owner.id
        if creator:
            props['creator_id'] = creator.id
        if score:
            props['score'] = score
        if date_due:
            props['date_due'] = date_due
        if category:
            props['category_id'] = category.id
        if swimlane:
            props['swimlane_id'] = swimlane.id

        (status, result) = self._send_template_request('updateTask', props)
        if status and result:
            return result
        else:
            return False

    def open(self):
        (status, result) = self._send_template_request('openTask', {'task_id': self.id})
        if status and result:
            return True
        else:
            return False

    def close(self):
        (status, result) = self._send_template_request('closeTask', {'task_id': self.id})
        if status and result:
            return True
        else:
            return False

    def remove(self):
        (status, result) = self._send_template_request('removeTask', {'task_id': self.id})
        if status and result:
            return True
        else:
            return False

    def move(self, column, position=1):
        (status, result) = self._send_template_request('moveTaskPosition', {'project_id': self.project.id,
                                                                            'task_id': self.id,
                                                                            'column_id': column.id,
                                                                            'position': position})
        if status and result:
            return result
        else:
            return False

    def create_comment(self, user, content):
        (status, result) = self._send_template_request('createComment', {'task_id': self.id,
                                                                         'user_id': user.id,
                                                                         'content': content})
        if status and result:
            return self.get_comment(result)
        else:
            return False

    def get_comment(self, comment_id):
        (status, result) = self._send_template_request('getComment', {'comment_id': comment_id})
        if status and result:
            return Comment(self, result)
        else:
            return None

    def get_all_comments(self):
        (status, result) = self._send_template_request('getAllComments', {'task_id': self.id})
        if status and result:
            comments = []
            for comment_info in result:
                comments.append(Comment(self, comment_info))
            return comments
        else:
            return []

    def create_subtask(self, title, user=None, time_estimated=None, time_spent=None, task_status=None):
        props = {'task_id': self.id, 'title': title}
        if user:
            props['user_id'] = user.id
        if time_estimated:
            props['time_estimated'] = time_estimated
        if time_spent:
            props['time_spent'] = time_spent
        if task_status:
            props['status'] = task_status
        (status, result) = self._send_template_request('createSubtask', props)
        if status and result:
            return self.get_subtask_by_id(result)
        else:
            return None

    def get_subtask_by_id(self, subtask_id):
        (status, result) = self._send_template_request('getSubtask', {'subtask_id': subtask_id})
        if status and result:
            return Subtask(self, result)
        else:
            return None

    def get_all_subtasks(self):
        (status, result) = self._send_template_request('getAllSubtasks', {'task_id': self.id})
        if status and result:
            subtasks = []
            for info in result:
                subtasks.append(Subtask(self, info))
            return subtasks
        else:
            return []

    def _file_get_contents_base64(self, filename):
        with open(filename) as f:
            file_contents = f.read()
        if file_contents:
            return base64.b64encode(file_contents)
        else:
            return None

    def create_file(self, filename, is_image, local_file):
        file_blob = self._file_get_contents_base64(local_file)
        is_image = '1' if is_image else '0'
        if file_blob:
            (status, result) = self._send_template_request('createFile', {'project_id': self.project.id,
                                                                          'task_id': self.id,
                                                                          'filename': filename,
                                                                          'is_image': is_image,
                                                                          'blob': file_blob})
            if status and result:
                return result
            else:
                return False
        else:
            return False

    def get_all_files(self):
        (status, result) = self._send_template_request('getAllFiles', {'task_id': self.id})
        if status and result:
            files = []
            for file_info in result:
                files.append(Attachment(self, file_info))
            return files
        else:
            return False

    def __unicode__(self):
        return u'Task{#' + six.text_type(self.id) + u', title: ' + self.title + \
               u', active: ' + six.text_type(self.is_active) + u'}'

    def __str__(self):
        return six.text_type(self).encode('utf-8')
