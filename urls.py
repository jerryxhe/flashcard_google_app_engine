# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import *

urlpatterns = patterns('',   (r'^$', 'views.search'),
                             (r'^s=(?P<key_word>\w+)/$', 'views.ssearch'),
                             (r'^view', 'views.view'),
                             (r'^add/$', 'views.add'),
                             (r'^all/$', 'views.all'),                             
                             (r'^note/$', 'views.note'),
                             (r'^books/$', 'views.books'),
                             (r'^addref/$', 'views.addref'),
                             (r'^post/$', 'views.post'),
                             (r'^postref/$', 'views.postref'),
                             (r'^image/(?P<img_id>(\w|-)+)/$', 'views.image' ),
                             (r'^download/$', 'views.download')
    # Example:    # (r'^foo/', include('foo.urls')),    
)
