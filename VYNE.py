#!/usr/bin/python3
import argparse
import requests
from colorama import init,Fore,Back,Style
from concurrent.futures import ThreadPoolExecutor
import os
import time as t
import json
import sys
import gc

init(autoreset=True)

red = Fore.RED
blue = Fore.BLUE
green = Fore.GREEN
white = Fore.WHITE
yellow = Fore.YELLOW
cyan = Fore.CYAN
cyan2 = Fore.LIGHTCYAN_EX

banner = f"""{cyan2}

	██╗   ██╗██╗   ██╗███╗   ██╗███████╗
	██║   ██║╚██╗ ██╔╝████╗  ██║██╔════╝
	██║   ██║ ╚████╔╝ ██╔██╗ ██║█████╗  
	╚██╗ ██╔╝  ╚██╔╝  ██║╚██╗██║██╔══╝  
	 ╚████╔╝    ██║   ██║ ╚████║███████╗
	  ╚═══╝     ╚═╝   ╚═╝  ╚═══╝╚══════╝
  
{cyan}     Vulnerability Yielding Network Enumerator v1.0

	 Developed with 🖤 by ShadowHunter-XD 
"""


print(banner)

parser = argparse.ArgumentParser(prog = "VYNE")

parser.add_argument("-w","--wordlist",help="Tarama için kullanılacak wordlist dosyasının yolu")
parser.add_argument("-u","--url",required=True,help="Hedef URL adresi (örneğin https://example.com)")
parser.add_argument("-X","--method",help="HTTP isteğinde kullanılacak metod (GET, POST, vs.)")
parser.add_argument("-o","--output",help="Tarama sonuçlarının kaydedileceği dosya yolu (örneğin: /root/Desktop/results/) NOT : Dosya adı girmeyiniz!")
parser.add_argument("--timeout",help="HTTP isteği için zaman aşımı süresi (saniye cinsinden, varsayılan: 15)",type=int)
parser.add_argument("-t","--thread",help="Paralel isteklerde kullanılacak thread sayısı (varsayılan: 5)",type=int)
parser.add_argument("-s","--subwordlist",help="Ek olarak Subdomain araması yapmak için wordlist dosyası belirtir." 
											  "(NOT : eğer bir wordlist girilmezse subdomain taraması yapılmaz)")
parser.add_argument("-fs","--firstsub",help="Önce subdomain arar (varsayılan: önce endpoint taraması)",action="store_true")
parser.add_argument("-noend","--noendpoint",help="Endpoint taraması yapmaz",action="store_true")
parser.add_argument("--status",help="İstenilen HTTP durum kodlarını virgülle ayırarak belirtir."
									"Sadece bu kodlara sahip yanıtlar loglanır." 
									"Örnek: --status 200,301,403"
									"(Varsayılan : 200,301,302)")
parser.add_argument("-K","--keys",help="POST isteği için zorunlu key worlisti")
parser.add_argument("-V","--values",help="POST isteği için zorunlu değer worlisti")
parser.add_argument("-D","--datas",help="POST isteği için eğer key ve value wordlisti girilmemişse, içinde hem key hem value bulunması gereken zorunlu wordlist"
										"(NOT : Eğer key ve value wordlistleri girilmemişse zorunludur)")
parser.add_argument("-U","--user-agent",help="User-Agent belirler"
											"(Varsayılan : Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36)")

args = parser.parse_args()


wordlist = []
subdomains = []
endpoints = []
subdomain_wordlist =[]
fake_subdomains = []
user_status_codes = []
fake_subs_body = []
post_responses = []
keys_wordlist = []
values_wordlist = []
datas_wordlist = []
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

headers ={
	"User-Agent" : args.user_agent if args.user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
	}

timeout_value = args.timeout if args.timeout else 15
thread = 5
http_req_type = "get"

def argument_settings():
	global timeout_value

	#values wordlisti kontrolü
	if args.values and not os.path.exists(args.values):
		print(red + "[!] Lütfen doğru bir values wordlisti girin")
		sys.exit(1)
	#datas wordlisti kontrolü
	if args.datas and not os.path.exists(args.datas):
		print(red + "[!] Lütfen doğru bir datas wordlisti girin")
		sys.exit(1)
	#keys wordlisti kontrolü
	if args.keys and not os.path.exists(args.keys):
		print(red + "[!] Lütfen doğru bir keys wordlisti girin")
		sys.exit(1)
	#noendpoint kontrolü
	if not args.noendpoint and not args.wordlist:
		print(red + "[!] --noendpoint parametresini kullanmıyorsanız, -w/--wordlist parametresi zorunludur.")
		sys.exit(1)

	#status kontorlü
	if args.status:
		status = args.status
		for code in status.split(","):
			user_status_codes.append(int(code))
	else:
		user_status_codes.extend([200,301,302])

	#subwordlist kontorlü
	if args.subwordlist and not os.path.exists(args.subwordlist):
		print(red + "[!] Lütfen doğru bir subdomain wordlisti girin")
		sys.exit(1)
	#wordlist kontorlü
	if args.wordlist and not os.path.exists(args.wordlist):
		print(red + "[!] Lütfen doğru bir endpoint wordlisti girin")
		sys.exit(1)

	#Thread kontorlü
	global thread
	
	if args.thread:
		thread = int(args.thread)
		if thread <= 0:
			print(red + "Hatalı thread değeri")
		elif thread >= 100:
			print(Back.RED + white + "UYARI : 1-Stabilizasyon hataları olabilir,\n2-hedef site IP adresini banlayabilir,\n3-işlem sınırın varsa çok hızlı dolar")
			t.sleep(2)
	else:
		thread = 5


	#method kontorlü
	global http_req_type
	
	if args.method:
		http_req_type = str(args.method)
		if http_req_type.lower() not in ("get","post"):
			print(red + "Method yalnızca 'GET' veya 'POST' olabilir") 
			sys.exit(1)
		elif http_req_type.lower() == "post":
			if args.datas:
				if args.values or args.keys:
					print(red + "[!] Yalnızca datas wordlisti ya da  keys ve values wordlisti girilebilir")
					sys.exit(1)
			else:
				if not args.values and args.keys:
					print(red + "[!] keys wordlisti var ama values wordlisti eksik")
					sys.exit(1)
				elif args.values and not args.keys:
					print(red + "[!] values wordlisti var ama keys wordlisti eksik")
					sys.exit(1)
				elif not args.keys and not args.values:
					print(red + "[!] Yalnızca datas wordlisti ya da  keys ve values wordlisti girilebilir")
					sys.exit(1)
	else:
		http_req_type = "get"

def wordlist_control():
	extensions = [".txt", ".lst", ".wordlist", ".dic", ".dict", ".list", ".wl", ".pwdlist"]
	
	#endpoint wordlist kontrolü
	if args.wordlist:
		user_wordlist = args.wordlist
		extension_bool = False
		for extension in extensions:
			if user_wordlist.endswith(extension):
				if os.path.exists(user_wordlist):
					print(green+"[+] endpoint Wordlisti bulundu.")
					extension_bool = True
					with open(user_wordlist,"r") as file:
						for line in file:
							wordlist.append(line.rstrip("\n"))
				else:
					print(red+"[!] endpoint Wordlisti bulunamadı.")
					sys.exit(1)

		if not extension_bool:
			print(red+"[!] uzantılar sadece.txt, .lst, .wordlist, .dic, .dict, .list, .wl, .pwdlist olabilir")
	elif args.wordlist is None and not args.noendpoint:
		print(red + "--noendpoint parametresini kullanmıyorsanız/Endpoint taraması yapacaksanız endpoint wordlisti girmek zorundasınız")
		sys.exit(1)
	#subdomain wordlist kontrolü
	if args.subwordlist:
		user_subdomain_wordlist = args.subwordlist
		extension_bool2 = False
		for ext in extensions:
			if user_subdomain_wordlist.endswith(ext):
				if os.path.exists(user_subdomain_wordlist):
					print(green+"[+] subdomain Wordlisti bulundu.")
					extension_bool2 = True
					with open(user_subdomain_wordlist,"r") as f:
						for line in f:
							subdomain_wordlist.append(line.rstrip("\n"))
				else:
					print(red+"[!] subdomain Wordlisti bulunamadı.")
					sys.exit(1)

		if not extension_bool2:
			print(red+"[!] uzantılar sadece.txt, .lst, .wordlist, .dic, .dict, .list, .wl, .pwdlist olabilir")
			sys.exit(1)
			
	#keys ve values wordlistleri kontrolü
	if args.keys and args.values:
		keys_file = args.keys
		values_file = args.values
		
		with open(keys_file,"r") as kf:
			for line in kf:
				keys_wordlist.append(line.rstrip("\n"))
		
		with open(values_file,"r") as vf:
			for line in vf:
				values_wordlist.append(line.rstrip("\n"))
		for key in keys_wordlist:
			for value in values_wordlist:
				datas_wordlist.append({key : value})

	#datas wordlisti kontrolü
	elif args.datas:
		datas_file = args.datas
		with open(datas_file,"r") as df:
			for line in df:
				line = line.strip()
				try:
					data = {}
					for d in line.split("&"):
						if "=" in d:
							k,v = d.split("=",1)
							data[k] = v
					datas_wordlist.append(data)
				except ValueError as e:
					print(red + f"[!] Hatalı satır atlandı -> {line}")
	
def url_check():
	url = args.url
	check_url = requests.get(url,timeout=timeout_value,headers=headers)
	if check_url.status_code == 200:
		print(green + "[+] Url bulundu")
	elif check_url.status_code in (301,302):
		location = check_url.headers.get("Location","Unknown")
		print(yellow + f"[+] girilen url şuraya yönlendiriyor -> {location}")
	else:
		print(red + "[-] Url yanlış veya çok yoğun")
		
def endpoint_scan(endpoint):
	gc.collect()
	url = args.url
	if not url.endswith("/"):
		url += "/"
	new_url = url + endpoint
	try:
		new_url_req = requests.get(new_url,timeout=timeout_value,headers=headers)
	except requests.RequestException as e:
		print(red + f"[!] İstek hatası : {e} -> {new_url}")
		return
	status = new_url_req.status_code
	url = new_url
	if new_url_req.status_code in user_status_codes:
		if {"url": url ,"status": status} not in endpoints:
			if new_url_req.status_code in (301,302):
				location = new_url_req.headers.get("Location","Unknown")
				if f"[{new_url_req.status_code}] {new_url} -> {[location]}" not in endpoints:
					print(yellow + f"[{new_url_req.status_code}] {new_url} -> {location}")
					endpoints.append({"url": url ,"status": status, "redirect": location})
			else:
				print(green + f"[{new_url_req.status_code}] {new_url}")
				endpoints.append({"url": url ,"status": status})

def url_post_request(data):
	gc.collect()
	url = args.url
	if not url.endswith("/"):
		url += "/"
	try:
		url_post_req = requests.post(url, timeout=timeout_value, data=data,headers=headers)
	except requests.RequestException as e:
		print(red + f"[!] İstek hatası : {e} -> gönderilen data : {data}")
		return
	if url_post_req.status_code in user_status_codes and  url_post_req.status_code in (301,302):
		location = url_post_req.headers.get("Location", "Unknown")
		print(yellow + f"[{url_post_req.status_code}] gönderilen data: {data}, {url} -> {location}")
		post_responses.append({"url": url,"status": url_post_req.status_code , "redirect": location,"data":data})
	elif url_post_req.status_code in user_status_codes:
		print(green + f"[{url_post_req.status_code}] gönderilen data: {data}")
		post_responses.append({"url": url,"status": url_post_req.status_code,"data": data})

def endpoint_json_operations():
	if args.method:
		http_req_type = args.method
		if http_req_type.lower() == "get":
			full_list = endpoints
			search_scope = "endpoints"
		elif http_req_type.lower() == "post":
			full_list = post_responses
			search_scope = "post-responses"
	else:
		full_list = endpoints
		search_scope = "endpoints"

	if len(endpoints) > 0 or len(post_responses) > 0:
		full_path = None
		json_path = args.output
		if json_path and not json_path.endswith("/"):
			json_path += "/"
		if os.path.exists(json_path):
			pass
		else:
			os.makedirs(json_path, exist_ok=True)
		
			
		for i in range(1,100):
			json_file_name = search_scope+str(i)+".json"
			if not os.path.exists(json_path+json_file_name):
				full_path = os.path.join(json_path,json_file_name)
				break
		if full_path is None:
			full_path = os.path.join(json_path, f"VYNE-{search_scope}1.json")
			
		with open(full_path,"w")as f:
			json.dump(full_list,f,indent=4)
			print(cyan + f"[+] {search_scope} için .json dosyası oluşturuldu -> {full_path}")
	else:
		print(cyan + f"[?] Hiç bir {search_scope} bulunmadığı için dosya oluşturulmadı")




def subdomain_json_operations():
	if len(subdomains) > 0:
		full_path = None
		json_path = args.output
		if json_path and not json_path.endswith("/"):
			json_path += "/"
		if not os.path.exists(json_path):
			os.makedirs(json_path, exist_ok=True)
		for i in range(1,100):
			json_file_name = "subdomains"+str(i)+".json"
			if not os.path.exists(json_path+json_file_name):
				full_path = os.path.join(json_path,json_file_name)
				break
		if full_path is None:
			full_path = os.path.join(json_path, "VYNE-subdomains1.json")
			
		full_list = subdomains

		with open(full_path,"w")as f:
			json.dump(full_list,f,indent=4)
		print(cyan + f"[+] subdomainler için .json dosyası oluşturuldu -> {json_path+json_file_name}")
	else:
		print(cyan + "[?] Hiç bir subdomain bulunamadığı için dosya oluşturulmadı")
		

global have_wildcard
have_wildcard = None

def wildcard_control():
	url = args.url
	if url.endswith("/"):
		url = url.rstrip("/")
	if url.startswith("https://"):
		new_url = url[len("https://"):]
	elif url.startswith("http://"):
		new_url = url[len("http://"):]
	#wildcard(fake subdomain) kontrolü
	for p in ["https://","http://"]:
		for char in "abcde12345":
			control_sub = p+char+"."+new_url
			try:
				control_response = requests.get(control_sub, timeout=timeout_value,headers=headers)
				control_body = control_response.text[:100]
				fake_subs_body.append(control_body)
			except requests.RequestException as e:
				pass
	if len(set(fake_subs_body)) <= 3:
		have_wildcard = True
		situation = "var"
	else:
		have_wildcard = False
		situation = "yok"
	print(f"wildcard kontrolü bitti, sonuç: {situation}")

global wildcard_scan

wildcard_scan = True

def subdomain_scan(sub):
	gc.collect()
	global wildcard_scan
	global have_wildcard
	if wildcard_scan:
		print("wildcard taranıyor")
		wildcard_control()
		if len(set(fake_subs_body)) <= 3:
			print(red + "[-] Wildcard var, cevaplar ona göre verilecek")
			have_wildcard = True
		else:
			print(green + "[+] Wildcard yok")
			have_wildcard = False
		wildcard_scan = False
	url = args.url
	if url.endswith("/"):
		url = url.rstrip("/")
	if url.startswith("https://"):
		new_url = url[len("https://"):]
	elif url.startswith("http://"):
		new_url = url[len("http://"):]
	else:
		return url
	subdomain = sub+"."+new_url
	for p in ["https://","http://"]:
		scanned_subdomain = p+subdomain
		try:
			scan_response =	requests.get(scanned_subdomain,timeout=timeout_value,headers=headers)
		except requests.RequestException as e:
			pass
		status = scan_response.status_code
		url = scanned_subdomain
		if scan_response.status_code in user_status_codes:
			body = scan_response.text[:100]
			if have_wildcard:
				if body not in fake_subs_body:
					if f"[{scan_response.status_code}] {subdomain}" not in subdomains:
						if scan_response.status_code in (301,302) and scan_response.status_code in user_status_codes:
							location = scan_response.headers.get("Location","Unknown")
							if f"[{scan_response.status_code}] {subdomain} -> {location}" not in subdomains:
								print(yellow + f"[{scan_response.status_code}] {subdomain} -> {location}")
								subdomains.append({"url": url ,"status": status, "redirect": location})
						elif scan_response.status_code in user_status_codes:
							print(green + f"[{scan_response.status_code}] {subdomain}")
							subdomains.append({"url": url ,"status": status})
			else:
				if f"[{scan_response.status_code}] {subdomain}" not in subdomains:
						if scan_response.status_code in (301,302) and scan_response.status_code in user_status_codes:
							location = scan_response.headers.get("Location","Unknown")
							if f"[{scan_response.status_code}] {subdomain} -> {location}" not in subdomains:
								print(yellow + f"[{scan_response.status_code}] {subdomain} -> {location}")
								subdomains.append({"url": url ,"status": status, "redirect": location})
						elif scan_response.status_code in user_status_codes:
							print(green + f"[{scan_response.status_code}] {subdomain}")
							subdomains.append({"url": url ,"status": status})
		else:
			fake_subdomains.append(scanned_subdomain)

def firstsub_control():
	if args.firstsub:
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for sub in subdomain_wordlist:
				executor.submit(subdomain_scan,sub)
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for endpoint in wordlist:
				executor.submit(endpoint_scan,endpoint)
	else:
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for endpoint in wordlist:
				executor.submit(endpoint_scan,endpoint)
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for sub in subdomain_wordlist:
				executor.submit(subdomain_scan,sub)

def for_post_firstsub_control():
	if args.firstsub:
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for sub in subdomain_wordlist:
				executor.submit(subdomain_scan,sub)
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for data in datas_wordlist:
				executor.submit(url_post_request,data)
	else:
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for data in datas_wordlist:
				executor.submit(url_post_request,data)
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for sub in subdomain_wordlist:
				executor.submit(subdomain_scan,sub)	



def working_order():
	global wildcard_scan
	global have_wildcard
	argument_settings()
	url_check()
	wordlist_control()
	if args.subwordlist:
		if wildcard_scan:
			print("wildcard taranıyor")
			wildcard_control()
			if len(set(fake_subs_body)) <= 3:
				print(red + "[-] Wildcard var, cevaplar ona göre verilecek")
				have_wildcard = True
			else:
				print(green + "[+] Wildcard yok")
				have_wildcard = False
			wildcard_scan = False
		if args.noendpoint:
			if http_req_type.lower() == "post":
				for_post_firstsub_control()
			if http_req_type.lower() == "get":
				with ThreadPoolExecutor(max_workers=thread) as executor:
					for sub in subdomain_wordlist:
						executor.submit(subdomain_scan,sub)
		else:
			if http_req_type.lower() == "post":
				for_post_firstsub_control()
			elif http_req_type.lower() == "get":
				firstsub_control()
	elif http_req_type.lower() == "post":
		if args.noendpoint:
			if http_req_type.lower() == "post":
				for_post_firstsub_control()
			if http_req_type.lower() == "get":
				with ThreadPoolExecutor(max_workers=thread) as executor:
					for sub in subdomain_wordlist:
						executor.submit(subdomain_scan,sub)
		else:
			if http_req_type.lower() == "post":
				for_post_firstsub_control()
			elif http_req_type.lower() == "get":
				firstsub_control()
	elif not args.subwordlist and  http_req_type.lower() == "post":
		for_post_firstsub_control()
	else:
		with ThreadPoolExecutor(max_workers=thread) as executor:
			for endpoint in wordlist:
				executor.submit(endpoint_scan,endpoint)
	
	if args.output:
		if args.subwordlist:
			if args.noendpoint:
				subdomain_json_operations()
			else:
				subdomain_json_operations()
				endpoint_json_operations()
		else:
			endpoint_json_operations()
	
try:
	working_order()
except KeyboardInterrupt as e:
	if args.output:
		if args.subwordlist:
			if args.noendpoint:
				subdomain_json_operations()
			else:
				subdomain_json_operations()
				endpoint_json_operations()
		else:
			endpoint_json_operations()
	print(Back.RED + white + "\nÇıkılıyor...")
	sys.exit(1)
except AttributeError as e:
	print(red + f"{e}")
	
	
	
