Welcome to elFinder for django documentation!
===================================================
	elFinder4django is a django connector for `elFinder <http://elfinder.org>`_ file manager.
	
.. note::

	this project only supports ``elFinder 2.x``, ``elFinder 1.x`` is not supported yet.
	
.. _ref-quick-installation:

Quick Installation Guide
------------------------

	#. simply, download and extract elfinder4django into temporary folder.
	#. copy the application folder called ``connector`` ( found in ``elfinder4django/elfindertest/connector`` ) inside your django project. 
	#. add `connector` in your ``INSTALLED_APPS`` inside :file:`settings.py` ::
	
		INSTALLED_APPS = (
			'connector',
			'all other apps',
			)
	#. open `urls.py` of your project. add new url config ::
	
		urlpatterns = patterns('',
			url(r'^elfinder/', include('projectname.connector.urls')), #where projectname is your project directory

			#Other Urls goes here
		)
	#. Make sure you set ``MEDIA_URL``, ``MEDIA_ROOT``, ``STATIC_URL``.
	#. Make sure you activate ``MEDIA_URL`` in your urls.py.
	#. download elFinder **version 2.x** from `elFinder <http://elfinder.org>`_  site (**note:** currently in 2.0-beta) . extract it in ``connect/static`` directory make sure you renamed it as ``elFinder``.
	#. if all these settings are Ok, run your server and point it to ``http://<host>:<port>/elfinder/``.
	#. you should see now all your ``MEDIA_ROOT`` sub files are now appeared. if not, make sure your django version is ``1.3``, django version ``<= 1.2`` is not supported until you install ``django-staticfiles`` .


.. _elFinder: http://elfinder.org