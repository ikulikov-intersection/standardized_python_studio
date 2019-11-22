##
import pandas, pyvisa, time, random 

psa_address = "TCPIP0::10.204.23.89::inst0::INSTR"
psg_address = "ASRL4::INSTR"
scope_adress = "TCPIP0::10.204.23.118::inst0::INSTR"

## ResourceManager initializer and basic/generic methods 

class visa_instrumment():
    def __init__(self, instrument_address):
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
## methods of measurments
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
            

    def single(self, trace=1, nsweep=1, max_hold=0):
        self.ocp_check()
        counter_sweep=0
        self.inst.write("TRAC%d:MODE WRIT"%(trace))
        if max_hold==1:
            self.inst.write("TRAC%d:MODE MAXH"%(trace))
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

## methods for set and get marker

class psa_marker():
    def __init__(self, psa, marker=1):
        self.inst=psa.inst
        self.marker=marker
        self.inst.write("CALC:MARK%d:STAT ON"%self.marker)
    
    def peak_search(self):
        self.inst.write("CALC:MARK%d:MAX"%(self.marker))
         
    def set_marker(self, freq):
        self.inst.write('CALC:MARK%d:X %d;' %(self.marker, freq))
        
    def get_marker(self):
        f=self.inst.query('CALC:MARK%d:X?;' %(self.marker))
        amp=self.inst.query('CALC:MARK%d:Y?;' %(self.marker))
        marker_val={'freq':[], 'ampl':[]}
        marker_val['freq'].append(f)
        marker_val['ampl'].append(amp)
        return marker_val
        
##run 

psa1=psa_e444x(psa_address)     
