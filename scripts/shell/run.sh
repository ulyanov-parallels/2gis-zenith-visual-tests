echo '***********************************'
echo '       ANDROID-SIDE RUNNER'
period=$1
timeout=$2
work_dir=$3
scenario=$4
app=$5
device_config=$6
script=$7
log=$8
echo 'period =' ${period}
echo 'timeout =' ${timeout}
echo 'work_dir =' ${work_dir}
echo 'scenario =' ${scenario}
echo 'app =' ${app}
echo 'device_config =' ${device_config}
echo 'script =' ${script}
echo 'log =' ${log}
sleep ${period}
am start -n ${app} -e working_directory ${work_dir} -e script ${script} -e configuration ${device_config} -e log ${log}
sleep $((3*period))
i=0
while ! [ -f ${work_dir}/finish.png ]; do
	sleep ${period}
	i=$((i+period))
	echo ${i}
	if [ $i -gt $timeout ]; then
		echo 'time =' ${i}
		echo 'timeout exit'
		exit 777
	fi
done
echo '***********************************'
