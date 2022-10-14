import os
from RfToF_Board_Anchor import Swarmbee
from peers import Target
import utime as time
import ujson

sync_word = 1
target_ = None
reset_ = False
save = False
range_amount = 1

"""
Need to define the order of the targets

"""
target_ = [0x00_00_00_01_F0_84, 0x00_00_00_01_EB_EE,0x00_00_00_01_F2_DC]
target_offsets_cm = [480,400,125]
range_amount = 3
sync_word = 1
reset_ = False
save = False

final_distance = []

me = Swarmbee(reset=reset_, verbose_mode=True)
# me.get_fac_settings(verbose_mode=True)
if not reset_:
    me.configure(syncword=sync_word, verbose_mode=True)
    me.get_fac_settings(reset=False, verbose_mode=True)

print("-" * 30)



#####
me = Swarmbee(reset=reset_, verbose_mode=True)
# me.get_fac_settings(verbose_mode=True)
if not reset_:
    me.configure(syncword=sync_word, verbose_mode=True)
    me.get_fac_settings(reset=False, verbose_mode=True)
# if save:
#     me.save()

print("-" * 30)

if target_ is not None:
    for j in range(len(target_)):
        print('{:012X}'.format(target_[j]))
        print('ranging {} times {:012X}'.format(range_amount, target_[j]))
        tar_get = Target(target_[j], target_offsets_cm[j], hint='Setup for Hackathon')
        ranges = []
        for i in range(range_amount):
            rr = me.range(tar_get)
            print("#{:>3d}:".format(i), rr)
            ranges.append(rr)
            time.sleep_ms(250)

        if range_amount > 1:
            r_res = [] # range result  for range_amount

            for range_ in ranges:
                try:
                    rr_ = range_.distance
                except AttributeError:
                    continue
                else:
                    r_res.append(rr_)
            try:
                ##modification by verifeckta
                outlier_percentage = int(len(ranges)*0.1)
                #print(outlier_percentage)
                r_res.sort()
                #print(r_res)
                start_val = outlier_percentage
                end_val = len(ranges)-outlier_percentage
                #print(start_val, end_val)
                good_values = r_res[start_val:end_val]
                final_distance.append(sum(good_values) / (len(ranges)-2*outlier_percentage))
                print("Good values:" , good_values)
                print("{} ranges: {:.1f} cm [{} ... {}]".format((len(ranges)-2*outlier_percentage), sum(good_values) / (len(ranges)-2*outlier_percentage), min(good_values), max(good_values)))
                ####
                print("All values :", r_res)
                print("{} ranges: {:.1f} cm [{} ... {}]".format(len(ranges), sum(r_res) / len(ranges), min(r_res), max(r_res)))
                print(final_distance)
                with open("reading.txt","w") as f:
                    f.write('\n'.join(str(distance) for distance in final_distance))
              
            except ValueError:
                ...
            except ZeroDivisionError:
                print('No Ranges received!')
    # me.deactivate()

def send(cmd):
    global me
    return me.cont_read(cmd)