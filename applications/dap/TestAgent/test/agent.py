import sys

from volttron.platform.vip.agent import Agent, PubSub, Core
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
from datetime import datetime
import ast

from . import settings

class TestAgent(Agent):
	def __init__(self, config_path, **kwargs):
		super(TestAgent, self).__init__(**kwargs)

	@PubSub.subscribe('pubsub', 'weather') #temperature/temp_c
	def on_heartbeat_topic(self, peer, sender, bus, topic, headers, message):
		print "TestAgent got\nTopic: {topic}, {headers}, Message: {message}".format(topic=topic, headers=headers, message=message)
		print "\n*********Dap: print 1 ok"
		print "\n*********Dap: message ****************** \n"	
		print message
		print type(message)
		print "/n*************************************"
		if True:
			message={'temperature':{'temp_c':10}}
			messageHisto= \
				{
					{headers_mod.DATE: datetime.utcnow().isoformat() + 'Z'},
					{
						[
							{
								"outsideAirTemperature ": str(message['temperature']['temp_c']),
								#"solarradiation ": str(message['cloud_cover']['solarradiation']),
								#"relativehumidity": str(message['pressure_humidity']['relative_humidity']),
								#"location": str(message['location']['observation_location']),
								#"date":str(message['time_topics']['observation_time'])
							},
							{
								"outsideAirTemperature ": {'units': 'degC', 'tz': 'UTC', 'type': 'float'},
								#"solarradiation ": {'units': 'W/m2', 'tz': 'UTC', 'type': 'float'},
								#"relativehumidity": {'units': '-', 'tz': 'UTC', 'type': 'float'},
								#"location": {'units': '-', 'tz': 'UTC', 'type': 'string'},
								#"date":{'units': '-', 'tz': 'UTC', 'type': 'string'}
							}
						]
					}
				}	
			print "\n*********Dap: messageHisto OK."
			print "******* Test Dap got: messageHisto: {messageHisto} *******".format(messageHisto=messageHisto)
			self.vip.pubsub.publish(peer='pubsub',topic='devices/',headers={'requesterID': 'agent1'},message=messageHisto)

	
	@Core.periodic(settings.HEARTBEAT_PERIOD)
	def send_request_weather(self):
		self.vip.pubsub.publish(peer='pubsub',topic='weather/request',headers={'requesterID': 'agent1'},message={'region':'Belgium','city':'Leuven'})

def main(argv=sys.argv):
	'''Main method called by the platform.'''
	utils.vip_main(TestAgent)


if __name__ == '__main__':
	# Entry point for script
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
