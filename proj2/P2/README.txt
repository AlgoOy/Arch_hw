运行环境：
	基于python3.9，没有调用第三方库，理论上python3.x都可以正常运行
使用方法：python MIPSsim.py {input_filepath/input_filename} [output_filepath/output_filename]
	input_filename是必选项，必须指定输入文件，output_filename是可选项，不指定output_filename时，默认输出文件名为“simulation.txt”
	其中，文件置于main.py目录下时，无需带路径
	置于其他目录下时，带绝对/相对路径
		示 例：
			python MIPSsim.py sample.txt
			python MIPSsim.py ../sample.txt
			python MIPSsim.py sample.txt simulation.txt
			python MIPSsim.py ../sample.txt ../simulation.txt