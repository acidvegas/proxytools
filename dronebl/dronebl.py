#!/usr/bin/env python
# Copyright (c) 2008 DroneBL contributors
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#      Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#      Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
#      Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

class DroneBLClient:
	"""Class for accessing DroneBL."""
	def __init__(self, rpckey=None, server="https://dronebl.org/RPC2"):
		self.server = server
		self.rpckey = rpckey
		self.submitList = ""

	def addIP(self, ip, type):
		"""Adds IP to DroneBL."""
		self.submitList += "\t<add ip='" + ip + "' type='" + str(type) + "' />\n";

	def lookupIP(self, ip):
		"""Adds a lookup request to the message."""
		self.submitList += "\t<lookup ip='" + ip + "' />\n"

	def makeRequest(self):
		"""Generates the request."""
		self.request = "<?xml version=\"1.0\"?>\n<request key='" + self.rpckey + "'>\n" + self.submitList + "</request>"

	def showRequest(self):
		"""Shows the request."""
		self.makeRequest()
		print self.request

	def makeConnection(self):
		"""Connects to the RPC server."""
		import urllib
		type, uri = urllib.splittype(self.server)
		self.__host, self.__handler = urllib.splithost(uri)

		import httplib
		self.connection = httplib.HTTPConnection(self.__host)

	def postRequest(self):
		"""Executes the request."""
		self.makeRequest()
		self.makeConnection()
		self.connection.putrequest("POST", self.__handler)
		self.connection.putheader("Content-Type", "text/xml")
		self.connection.putheader("Content-Length", str(int(len(self.request))))
		self.connection.endheaders()
		self.connection.send(self.request)
		self.__response = self.connection.getresponse()

	def printResponse(self):
		"""Display the XML response."""
		print self.__response.read()

