#!/usr/bin/env python
#-*- coding:utf-8 -*-

import httplib, urllib, urllib2
import time
import sys,os
import socket
import re
import json

username = 'your_email@gmail.com'
password = 'your_password'
format = 'json'

domain = [u'www.you_domain_name.com'] 

def get_domain_info(domain):
  domain_split = domain.split('.')
  domain_split_len = len(domain_split)
  main_domain = domain_split[domain_split_len - 2] + '.' + domain_split[domain_split_len - 1]
  return main_domain,domain

params = {'login_email':username,'login_password':password,'format':format}

def send_request(action, params, method = 'POST'):
  headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
  conn = httplib.HTTPSConnection("dnsapi.cn")
  conn.request(method, '/' + action, urllib.urlencode(params), headers)
  response = conn.getresponse()
  data = response.read()
  conn.close()
  if response.status == 200:
    return data
  else:
    return None

def get_my_domain_id():
  data = send_request('Domain.List',params)
  data = json.loads(data)
  domainlist = data.get('domains')
  domaninfo = {}
  for d in domainlist:
    domaninfo[d.get('name')] = d.get('id')
  return domaninfo

def get_my_domain_record_id(domain_id):
  params['domain_id'] = domain_id
  data = send_request('Record.List',params)
  data = json.loads(data)
  if data.get('code') == '10':
    return None
  domainname = data.get('domain').get('name')
  
  record_list = data.get('records')
  record = {}
  for r in record_list:
    if r.get('type') == 'A':
      key = r.get('name') != '@' and r.get('name') + '.' + domainname or domainname
      record[key] = {'id':r.get('id'),'value':r.get('value'),'line_id':r.get('line_id')}
  return record

def update_dns_record(domain,domain_id,record_id,ip):
  params['domain_id'] = domain_id
  params['record_id'] = record_id
  params['sub_domain'] = domain
  params['record_line'] = '默认'
  params['value'] = ip
  
  data = send_request('Record.Ddns',params)
  
def get_public_ip():
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    ip = sock.recv(16)
    sock.close()
    return ip

def get_domain(domain):
  main_domain,sub_domain = get_domain_info(domain)
  domain_id = my_domain_id_list.get(main_domain)
  record_list = get_my_domain_record_id(domain_id)
  if record_list == None:
    return None
  rocord_info = record_list.get(sub_domain)
  record_ip = rocord_info.get('value')
  record_id = rocord_info.get('id')
  return sub_domain,record_ip,record_id,domain_id

if __name__ == '__main__':
  my_domain_id_list = get_my_domain_id()
  try:
    for dm in domain:
      domain_data = get_domain(dm)
      if domain_data == None:
        continue
      dns_domain,dmain_ip,record_id,domain_id = domain_data
      domain_name = dns_domain.split('.')[0]
      ip = get_public_ip()
      if ip == dmain_ip:
        print "IP doesn't change"
        continue
      else:
        update_dns_record(domain_name,domain_id,record_id,ip)
  except:
    pass