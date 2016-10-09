# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2015, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#	list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#	this list of conditions and the following disclaimer in the documentation
#	and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

#}}}

from __future__ import absolute_import

from datetime import datetime
import logging
import random
import sys

from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod




utils.setup_logging()
_log = logging.getLogger(__name__)

'''
Structuring the agent this way allows us to grab config file settings 
for use in subscriptions instead of hardcoding them.
'''

def subscriber_agent(config_path, **kwargs):
	config = utils.load_config(config_path)
	oat_point= config.get('oat_point')
	all_topic = config.get('all_topic')
	
	
	class ExampleSubscriber(Agent):
		'''
		This agent demonstrates usage of the 3.0 pubsub service as well as 
		interfacting with the historian. This agent is mostly self-contained, 
		but requires the histoiran be running to demonstrate the query feature.
		'''
	
		def __init__(self, **kwargs):
			super(ExampleSubscriber, self).__init__(**kwargs)
	
		@Core.receiver('onsetup')
		def setup(self, sender, **kwargs):
			# Demonstrate accessing a value from the config file
			self._agent_id = config['agentid']
	
	

		@PubSub.subscribe('pubsub', all_topic)
		def match_device_all(self, peer, sender, bus,  topic, headers, message):
			'''
			This method subscribes to all points under a device then pulls out 
			the specific point it needs.
			The first element of the list in message is a dictionairy of points 
			under the device. The second element is a dictionary of metadata for points.
			'''
					   
			print("Whole message", message)
			
			#The time stamp is in the headers
			print('Date', headers['Date'])
			
			#Pull out the value for the point of interest
			print "******* Dap ok:"
			print message[0]
			print("Value", message[0]['outsideAirTemperature'])
			
			#Pull out the metadata for the point
			print('Unit', message[1]['outsideAirTemperature']['units'])
			print('Timezone', message[1]['outsideAirTemperature']['tz'])
			print('Type', message[1]['outsideAirTemperature']['type'])
		   

	
		@PubSub.subscribe('pubsub', oat_point)
		def on_match_OAT(self, peer, sender, bus,  topic, headers, message):
			'''
			This method subscribes to the specific point topic.
			For these topics, the value is the first element of the list 
			in message.
			'''
			
			print("Whole message", message)
			print('Date', headers['Date'])
			print("Value", message[0])
			print("Units", message[1]['units'])
			print("TimeZone", message[1]['tz'])
			print("Type", message[1]['type'])
			
		
		@PubSub.subscribe('pubsub', '')
		def on_match_all(self, peer, sender, bus,  topic, headers, message):
			''' This method subscibes to all topics. It simply prints out the 
			topic seen.
			'''
			print(topic)
#	 
		# Demonstrate periodic decorator and settings access
		
		@Core.periodic(10)
		def lookup_data(self):
			'''
			This method demonstrates how to query the platform historian for data
			This will require that the historian is already running on the platform.
			'''
			
			try: 
				result = self.vip.rpc.call(
										   #Send this message to the platform historian
										   #Using the reserved ID
										   'platform.historian', 
										   #Call the query method on this agent
										   'query', 
										   #query takes the keyword arguments of:
										   #topic, then optional: start, end, count, order
#											start= "2015-10-14T20:51:56",
										   topic=query_point,
										   count = 20,
										   #RPC uses gevent and we must call .get(timeout=10)
										   #to make it fetch the result and tell 
										   #us if there is an error
										   order = "FIRST_TO_LAST").get(timeout=10)
				print('Query Result', result)
			except Exception as e:
				print ("Could not contact historian. Is it running?")
				print(e)
		
		@Core.periodic(10)
		def pub_fake_data(self):
			''' This method publishes fake data for use by the rest of the agent.
			The format mimics the format used by VOLTTRON drivers.
			
			This method can be removed if you have real data to work against.
			'''
			
			# Fake message
			message = \
				{'temperature': 
					{
						'windchill_f': 'NA', 'heat_index_f': 'NA', 'temp_f': 57.9, 'heat_index_string': 'NA', 'temp_c': 14.4, 'feelslike_c': '14.4', 'windchill_string': 'NA', 'feelslike_f': '57.9', 'heat_index_c': 'NA', 'windchill_c': 'NA', 'feelslike_string': '57.9 F (14.4 C)', 'temperature_string': '57.9 F (14.4 C)'
					}, 
				'cloud_cover': 
					{
						'visibility_mi': '6.2', 'solarradiation': '--', 'weather': 'Partly Cloudy', 'visibility_km': '10.0', 'UV': '1'
					}, 
				'location': 
					{
						'display_location': {'city': 'Leuven', 'full': 'Leuven, Belgium', 'magic': '10', 'state_name': 'Belgium', 'zip': '00000', 'country': 'BX', 'longitude': '4.69999981', 'state': u'', 'wmo': '06451', 'country_iso3166': 'BE', 'latitude': '50.88333511', 'elevation': '21.00000000'}, 'local_tz_long': 'Europe/Brussels', 'observation_location': {'city': 'Mechelsevest, Leuven', 'full': 'Mechelsevest, Leuven, ', 'elevation': '0 ft', 'country': 'BX', 'longitude': '4.686095', 'state': u'', 'country_iso3166': 'BE', 'latitude': '50.885235'}, 'station_id': 'ILEUVEN74'}, 
				 'time': 
				 	{
						'local_tz_offset': '+0200', 'local_epoch': '1476002247', 'observation_time': 'Last Updated on October 9, 10:36 AM CEST', 'local_tz_short': 'CEST', 'observation_epoch': '1476002189', 'local_time_rfc822': 'Sun, 09 Oct 2016 10:37:27 +0200', 'observation_time_rfc822': 'Sun, 09 Oct 2016 10:36:29 +0200'
					}, 
				 'pressure_humidity': 
				 	{
						'relative_humidity': '68%', 'pressure_mb': '1026', 'pressure_trend': '0'
					}, 	
				 'precipitation': 
				 	{
						'dewpoint_string': '48 F (9 C)', 'precip_1hr_in': '-999.00', 'precip_today_in': '0.00', 'precip_today_metric': '0', 'precip_today_string': '0.00 in (0 mm)', 'dewpoint_f': 48, 'dewpoint_c': 9, 'precip_1hr_string': '-999.00 in ( 0 mm)', 'precip_1hr_metric': ' 0'
					}, 
				 'wind': 
				 	{
						'wind_degrees': 54, 'wind_kph': 1.0, 'wind_gust_mph': '1.2', 'wind_mph': 0.6, 'wind_string': 'Calm', 'pressure_in': '30.30', 'wind_dir': 'NE', 'wind_gust_kph': '1.9'
					}
				}

			# message with all points: Device format
			all_message= \
				[
					{
						"outsideAirTemperature": message['temperature']['temp_c'],
						"solarradiation": message['cloud_cover']['weather'],
						"relativehumidity": message['pressure_humidity']['relative_humidity'],
						"location": message['location']['observation_location'],
						"date":message['time']['observation_time']
					},
					{
						"outsideAirTemperature": {'units': 'degC', 'tz': 'UTC', 'type': 'float'},
						"solarradiation": {'units': 'W/m2', 'tz': 'UTC', 'type': 'str'},
						"relativehumidity": {'units': '-', 'tz': 'UTC', 'type': 'str'},
						"location": {'units': '-', 'tz': 'UTC', 'type': 'str'},
						"date": {'units': '-', 'tz': 'UTC', 'type': 'str'}
					}
				]
																						
			#Outside air temperature message
			oat_message = [message['temperature']['temp_c'], {'units': 'degC', 'tz': 'UTC', 'type': 'float'}]

			
			#Create timestamp
			now = datetime.utcnow().isoformat(' ') + 'Z'
			headers = {
				headers_mod.DATE: now
			}
			
			#Publish messages
			self.vip.pubsub.publish(
				'pubsub', all_topic, headers, all_message)
			
			self.vip.pubsub.publish(
				'pubsub', oat_point, headers, oat_message)

	return ExampleSubscriber(**kwargs)
def main(argv=sys.argv):
	'''Main method called by the eggsecutable.'''
	try:
		utils.vip_main(subscriber_agent)
	except Exception as e:
		_log.exception('unhandled exception')


if __name__ == '__main__':
	# Entry point for script
	sys.exit(main())
