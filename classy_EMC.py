import pandas, pyvisa, time, random 




psa_address = "TCPIP0::10.204.23.89::inst0::INSTR"
psg_address = "ASRL4::INSTR"
scope_adress = "TCPIP0::10.204.23.118::inst0::INSTR"



class visa_instrumment():
    def __init__(self, instrument_address):
        print("sss")
        self.inst=pyvisa.ResourceManager().open_resource('%s' %(instrument_address))
        self.inst.read_termination = '\n'
        self.inst.timeout = 5000
    def ocp_check(self):
        a=0
        while a !=1:
            try:
                a = int(self.inst.query("*OPC?"))
            except:
                time.sleep(1)
                print("waiting")
        a=0
    def filename_gen(self):
        self.filename = str(int(random.random()*10000000))


class psa_marker(psa_e444x):
    def __init__(self, marker):
        self.inst.write("CALC:MARK%d:STAT:ON"%marker)
        
        
    def get_marker(self, marker=1):
        f=self.inst.query('CALC:MARK%d:X?;' %(marker))
        amp=self.inst.query('CALC:MARK%d:Y?;' %(marker))
        marker={'freq':[], 'ampl':[]}
        marker['freq'].append(f)
        marker['ampl'].append(amp)
        return marker
        

class psa_e444x(visa_instrumment):
    def save(self, path, local_filename, trace=1, csv=1, screen=1):
        self.filename_gen()
        if screen==1:
            self.inst.write("MMEM:STOR:SCR 'C:\%s.GIF'" %(self.filename))
            capture = self.inst.query_binary_values(message=":MMEM:DATA? 'C:\%s.GIF'" %(self.filename), container=list, datatype='c')
            with open(r"%s%s.GIF" %(path, local_filename), 'wb') as fp:
                for byte in capture:
                    fp.write(byte)
                fp.close()
            self.inst.write("MMEMory:DELete 'C:\%s.GIF'" %(self.filename))
        else:
            print("NO SCREEN WILL BE SAVE.")
        if csv==1:
            self.inst.write(":MMEM:STOR:TRAC TRACE%d,'C:\%s.CSV'" %(trace, self.filename))
            capture = self.inst.query_binary_values(message=":MMEM:DATA? 'C:\%s.CSV'" %(self.filename), container=list, datatype='c')
            with open(r"%s%s.CSV" %(path, local_filename), 'wb') as fp:
                for byte in capture:
                    fp.write(byte)
                fp.close()       
            self.inst.write("MMEMory:DELete 'C:\%s.CSV'" %(self.filename))
        else:
            print("NO TRACE WILL BE SAVE")
            
    def single(self, nsweep, max_hold=0):
        self.ocp_check()
        counter_sweep=0
        if max_hold==1:
            self.inst.write("TRAC:MODE MINH")
            self.inst.write("TRAC:MODE MAXH")
        while counter_sweep!=nsweep:
            self.inst.write("TRIG:SOUR IMM")    
            self.inst.write("INIT:CONT OFF")
            self.inst.write("INIT:IMM")
            self.ocp_check()    
            self.inst.write("DISP:FSCR ON")
            counter_sweep=counter_sweep+1
    def main_set(self, freq_start, freq_stop, rbw, att, rlev, point_name, units, points):
        self.inst.write("UNIT:POW %s" %(units))
        self.inst.write("SWE:POIN %d" %(points))
        self.inst.write("POW:ATT %ddb" %(att))
        self.inst.write("DISP:WIND:TRAC:Y:RLEV %f %s" %(rlev, units))
        self.inst.write("BAND %dHz" %(rbw))
        self.inst.write("FREQ:STAR %d Hz" %(freq_start))
        self.inst.write("FREQ:STOP %d Hz" %(freq_stop))







psa1=psa_e444x(psa_address)     
