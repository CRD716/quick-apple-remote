import asyncio
import pyatv
import pyatv.exceptions
from pyatv.storage.file_storage import FileStorage
import random

storage = FileStorage

async def scan(loop):
	atvs = await pyatv.scan(loop)
	for index, atv in enumerate(atvs):
		print(f"[{index}] Name: {atv.name}, Address: {atv.address}")
	print("Select the device to pair to (Just the number before the information): ")
	selection = int(input())
	return atvs[selection]

async def pairingHandler(loop, deviceconfig):
	#TODO: this is garbage. some commands are only on certain protocols, and we should first scan for the available ones, then let the user decide which to use.
	try:
		pairing = await pyatv.pair(deviceconfig, pyatv.const.Protocol.MRP, loop)
	except pyatv.exceptions.NoServiceError:
		try:
			print("MRP Service unavailable, falling back to DMAP.")
			pairing = await pyatv.pair(deviceconfig, pyatv.const.Protocol.DMAP, loop)
		except pyatv.exceptions.NoServiceError:
			print("MRP and DMAP Service unavailable, falling back to Companion.")
			pairing = await pyatv.pair(deviceconfig, pyatv.const.Protocol.Companion, loop)
	
	await pairing.begin()

	if pairing.device_provides_pin:
		pin = int(input("Enter PIN: "))
		pairing.pin(pin)
	else:
		pin = random.randint(1000, 9999) #TODO: Not great, any codes that start with 0 aren't possible
		pairing.pin(pin)
		input("Enter this PIN on the device: "+pin)

	await pairing.finish()

	if pairing.has_paired:
		print("Paired with device!")
		print("Credentials:", pairing.service.credentials)
	else:
		print("Did not pair with device!")

	await pairing.close()

async def connect(loop, deviceconfig):
	return await pyatv.connect(deviceconfig, loop)

async def control(loop, atv:pyatv.interface.AppleTV):
	help_text = """
	--Tool Commands--
	exit_remote
	--Power Commands--
	power_on
	power_off
	--Audio Commands--
	volume_up
	volume_down
	--Remote Commands--
	channel_up (Companion Protocol Only)
	channel_down (Companion Protocol Only)
	up
	down
	left
	right
	home
	home_hold
	menu
	top_menu
	play
	pause
	play_pause
	next
	previous
	screensaver (Companion Protocol Only)
	select
	set_position (TODO)
	set_repeat (TODO)
	set_shuffle (TODO)
	skip_forward
	skip_backward
	stop
	"""
	print(help_text)
	
	while (True):
		action = input()

		match action:
			case "exit_remote":
				break
			case "power_on":
				await atv.power.turn_on()
			case "power_off":
				await atv.power.turn_off()
			case "volume_up":
				await atv.audio.volume_up()
			case "volume_down":
				await atv.audio.volume_down()
			case "up":
				await atv.remote_control.up()
			case "down":
				await atv.remote_control.down()
			case "left":
				await atv.remote_control.left()
			case "right":
				await atv.remote_control.right()
			case "home":
				await atv.remote_control.home()
			case "home_hold":
				await atv.remote_control.home_hold()
			case "menu":
				await atv.remote_control.menu()
			case "top_menu":
				await atv.remote_control.top_menu()
			case "play":
				await atv.remote_control.play()
			case "pause":
				await atv.remote_control.pause()
			case "play_pause":
				await atv.remote_control.play_pause()
			case "next":
				await atv.remote_control.next()
			case "previous":
				await atv.remote_control.previous()
			case "screensaver":
				await atv.remote_control.screensaver()
			case "select":
				await atv.remote_control.select()
			case "skip_forward":
				await atv.remote_control.skip_forward()
			case "skip_backward":
				await atv.remote_control.skip_backward()
			case "stop":
				await atv.remote_control.stop()
			case _:
				print(help_text)

async def main():
	loop = asyncio.get_event_loop()
	storage = FileStorage("pyatv.json", loop)
	await storage.load()

	deviceconfig = await scan(loop) #Scan for devices
	await pairingHandler (loop, deviceconfig) #Pair
	atv = await connect(loop, deviceconfig) #Connect
	await control(loop, atv) #Run commands
	await asyncio.gather(*atv.close()) #Wait to close everything
	await storage.save() #Save data


if __name__ == "__main__":
	asyncio.run(main())