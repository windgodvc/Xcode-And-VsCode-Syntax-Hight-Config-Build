#!/usr/bin/python
# 					author:windgodvc 
# -*- coding: UTF-8 -*-
#  Lua.xclangspec 文件源自于:https://github.com/breinhart/Lua-In-Xcode/blob/master/Lua.xclangspec
#  
import re
import os
import sys
import time


#\w+\s\w+::.*  这个匹配类 函数 要语法判断 下 是否有return or ;.如果有就不是函数.
#\w+\s\w+\s\w+[:]:\w+\(.*  继续改进...匹配类函数.
#\w+\s\w+[:]:\w+\([^"].* 完美...
#[^\s].*::\w+\([^"](?!;).*
#.*::\w+\([^"].*
#.*\w+(.*)\s{
#([^\s].*\w+(.*)\s{)  	这个正则可匹配出 静态函数  和 const 函数 和 类函数 ...可是 效率 太低了 不建议使用...
#([^\s].*\w+::(.*)\s{)  这个是上面的改进型...速度 快N倍因为少了很多匹配 如静态函数 和 普通函数.
#
#
#\w+\s\w+\s\w+\(.* 这个是匹配静态函数 的 要自己 删除 {
# 
# # class    AAA    :       {func }
# 	class\s+(\w+)\s*:?\s*(.*?)\s*{(.*?)}

# 	void       func(  int a, int b)
# 	\w+[\s\*&]+(\w+)\((.*?)\)', re.S)
# 	Static Function
# 	\s+static\s+\w+[\s\*&]+(\w+)\((.*?)\)

# 	 typedef enum {}typename;
# 	\s*enum[\s\S]*?{([\s\S]*?)}
# 	\s+([_a-zA-Z][_a-zA-Z0-9]*)

reslist = []
filterlist = [".hpp",".lua"]
AllFileApi = []
LuaSyntaxHead = """
(

/****************************************************************************/
// MARK: Lua keywords
/****************************************************************************/
	{
		Identifier = "xcode.lang.lua.identifier";
		Syntax = {
            StartChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_[";
            Chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_?[]";
            Words = (\n"""

class FunctionInfo:
	"""docstring for FunctionInfo"""
	def __init__(self,first,second):
		self.Funname = first; #function Name.
		self.namespace = second; # class namespace .


def getDirFile(filepath):
    #遍历filepath下所有文件，包括子目录
    files = os.listdir(filepath)
    for fi in files:
      fi_d = os.path.join(filepath,fi)
      if os.path.isdir(fi_d):
        getDirFile(fi_d)
      else:
      	flag = False;
      	for value in filterlist:
      		if os.path.join(filepath,fi_d).rfind(value) != -1:
      			flag = True;
      			#print os.path.join(filepath,fi_d),value
      			break;
        if not flag:
        	reslist.append(os.path.join(filepath,fi_d))

def readFile(file):
	f = open(file,"r");
	content = f.read();
	f.close();
	return content;

def writeFile(file,content):
	f = open(file,"w");
	f.write(content);
	f.close();

def getApi(file):
	f = open(file);
	if f:
		content = f.read();
		pat = re.compile("int\s(lua_cocos2dx_+([^\(]+))");
		f.close();
		return pat.findall(content),getCocosNameSpaceFromFileName(file);
	else:
		f.close();
		return "";

def getApiEx(file):
	content = readFile(file);
	pat = re.compile("([^\s].*\w+::(.*)\s{)");
	return pat.findall(content),getCocosNameSpaceFromFileName(file);

def getCocosNameSpace(str):
	if str.find("ccexp.") != -1:
		return "ccexp.";
	elif str.find("sp.") != -1:
		return "sp.";
	elif str.find("ccs.") != -1:
		return "ccs.";
	elif str.find("ccui.") != -1:
		return "ccui.";
	elif str.find("cc.") != -1:
		return "cc.";
	else :
		return "";

def getCocosNameSpaceFromFileName(file):
	if file.find("lua_cocos2dx_ui_auto.cpp") != -1 :
		return "ccui.";
	elif file.find("lua_cocos2dx_studio_auto.cpp") != -1:
		return "ccs.";
	elif file.find("lua_cocos2dx_spine_auto.cpp") != -1:
		return "sp.";
	elif file.find("lua_cocos2dx_experimental_webview_auto.cpp") != -1 or file.find("lua_cocos2dx_experimental_video_auto.cpp") != -1 or file.find("lua_cocos2dx_experimental_auto.cpp") != -1 or file.find("lua_cocos2dx_audioengine_auto.cpp") != -1:
		return "ccexp.";
	else:
		return "cc.";



def getLuaFunName(str):
	split = str.split("_");
	length = len(split);
	return split[length - 2] + ":" + split[length - 1];

#  去重复.
def deleteRep(Apilist):
	return 0;

def IsClassFunction(var):
	if len(var) <= 0:
		return False;
	var = var.strip();
	var = var.replace("{","");
	if var.find("=") != -1 and var.find("/*") == -1:
		return False;
	if var[len(var) - 1] == "," or var[0] == "," or var[0] == ":" or var[0] == "\"":
		return False;
	if var.find(";") != -1 or var.find(" ") == -1 or var.find("if (") != -1 or var.find("if(") != -1 or var.find("while (") != -1 or var.find("} else") != -1 or var.find("}") != -1:
		return False;
	return True;
		
def FormatClassFunction(var):
	if len(var) <= 0:
		return var;
	if var[0] == ",":
		return "";
	if var.find(" ") == -1:
		return "";
	var = var.replace("{","");
	var = var.strip();
	return var;

def getClassFunctionArg(var):
	# 转到lua 语法
	if len(var) <= 0:
		return var;
	var = var.replace("::",":");
	# 删除掉首或尾的 const.
	var = var.replace("const","");
	index_0 = var.find("(");
	index_1 = var.find(")",index_0);
	if index_0 == -1 or index_1 == -1 or var.find("()") != -1:
		return var;
	split = var[index_0 + 1:index_1].split(","); 
	data = ""
	index = 0;
	flag = ",";
	for value in split:
		index += 1;
		if index >= len(split):
			flag = "";
		value = value.strip();
		data += "${%d:%s}%s"%(index,value,flag);
	# 替换成配置文件语法
	data = var[0:var.find("(")] + "(" + data + ")";
	# 不取出返回值.
	return data[data.find(" "):len(data)].strip();

def parse(dir):
	filterlist = [".hpp",".lua"]
	getDirFile(dir)
	for v in reslist:
		funcApi,namespace = getApi(v)
		for s in funcApi:
			AllFileApi.append(FunctionInfo(getLuaFunName(s[0]),namespace));

	if len(AllFileApi) <= 0:
		return False;
	else:
		return True;

def parseAllCocosFile(dir):
	global reslist;
	global filterlist;
	global AllFileApi;
	reslist = []
	AllFileApi = []
	filterlist = ["scripting",".h",".mm",".pro",".xml",".inl",".mk",".m","proj.",".frag",".vert",".java",".DS_Store",".aidl",".txt",".classpath"]
	getDirFile(dir);
	data = "";
	number = 0;
	for var in reslist:
		number += 1;
		funcApi,namespace = getApiEx(var);
		for var in funcApi:
			var = FormatClassFunction(var[0]);
			if IsClassFunction(var):
				data += var + "\n";
				#print "哟...",var;
				AllFileApi.append(var);
		time.sleep(0.1);
		#if number >= 20:
		#	break;
	writeFile(sys.path[0] + "/CocosAllClassSyntax.json",data);
	return True;

def readLuaSyntaxFile(dir):
	f = open(dir);
	content = f.read();
	f.close();
	return content;

#  生成 Xcode 的 Lua 着色配置文件
def outToXcodeSyntaxFile():
	data = "";
	f = open(sys.path[0] + "/CocosLua.xclangspec","w");
	f.write(LuaSyntaxHead);
	for value in AllFileApi:
		data +="                \"%s()\",\n"%(value.namespace + value.Funname);
	f.write(data);
	f.write(readLuaSyntaxFile(sys.path[0] + "/LuaFile.xclangspec"));
	f.close();

#  生成 VsCode 的 Lua 着色配置文件
def outToVsCodeSyntaxFile():
	data = ""
	str = "";
	FunctionName = ""
	arg = "$1";
	resultList = []
	#  先生成语法 然后 加入到容器中 然后去重复 然后输出到文件 .
	for value in AllFileApi:
		if value.Funname.find(":constructor") != -1:
			value.Funname = value.Funname.replace(":constructor",":create");
		if value.Funname.find("get") != -1:
			arg = "";
		else:
			arg = "$1";
		str = value.namespace + value.Funname;
		FunctionName = value.Funname.split(":")[1];
		data = """
		 "%s": {
			"prefix": "%s",
			"body": [
				"%s(%s)"
			],
			"description": "%s"
		},"""%(str,str,str,arg,str);
		resultList.append(data);

		# 输出函数名不带类名...
		data = """
		 "%s": {
			"prefix": "%s",
			"body": [
				"%s(%s)"
			],
			"description": "%s"
		},"""%(FunctionName,FunctionName,FunctionName,arg,FunctionName);
		resultList.append(data);


	# 	data +="""
	#  "%s": {
	# 	"prefix": "%s",
	# 	"body": [
	# 		"%s(%s)"
	# 	],
	# 	"description": "%s"
	# },
	# "%s": {
	# 	"prefix": "%s",
	# 	"body": [
	# 		"%s(%s)"
	# 	],
	# 	"description": "%s"
	# },"""%(str,str,str,arg,str,FunctionName,FunctionName,FunctionName,arg,FunctionName);
	
	#  去重复....
	resultList = list(set(resultList))

	data = "";

	for value in resultList:
		data += value;

	f = open(sys.path[0] + "/lua.json","w");
	f.write(data);
	f.close();

#  生成 VsCode 的 Lua 着色配置文件
def AllCocos2dClassOutToVsCodeSyntaxFile():
	data = ""
	str = "";
	global AllFileApi;
	resultList = []
	#  先生成语法 然后 加入到容器中 然后去重复 然后输出到文件 .
	for value in AllFileApi:
		argFunc = getClassFunctionArg(value);
		data = """
		 "%s": {
			"prefix": "%s",
			"body": [
				"%s"
			],
			"description": "%s"
		},"""%(value,value,argFunc,value);
		resultList.append(data);

		# functname = argFunc.split(":")[1];
		# # 输出函数名不带类名...
		# data = """
		#  "%s": {
		# 	"prefix": "%s",
		# 	"body": [
		# 		"%s"
		# 	],
		# 	"description": "%s"
		# },"""%(functname,functname,functname,functname);
		resultList.append(data);
	
	#  去重复....
	resultList = list(set(resultList))

	data = "";

	for value in resultList:
		data += value;

	f = open(sys.path[0] + "/Cocoslua.json","w");
	f.write(data);
	f.close();
		

class ParseFile(object):
	"""docstring for ParseFile"""
	def __init__(self):
		super(ParseFile, self).__init__()
	
	def parseToLuaFile(self):
		if parse("/Applications/Cocos/frameworks/cocos2d-x-3.8.1/cocos/scripting/lua-bindings/auto/"):
			outToXcodeSyntaxFile();
			outToVsCodeSyntaxFile();

	def parseC_Plug_PlugToLua(self):
		parseAllCocosFile("/Applications/Cocos/frameworks/cocos2d-x-3.8.1/cocos/")
		AllCocos2dClassOutToVsCodeSyntaxFile();	
		



if __name__ == '__main__':
	#  解析类...
	item = ParseFile();
	item.parseToLuaFile();
	item.parseC_Plug_PlugToLua();
	print "总共:%d个文件."%(len(reslist));
	print "总共:%d个Api函数."%(len(AllFileApi));
