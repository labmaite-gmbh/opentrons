import os
import re
import shlex
import stat
import subprocess
from dataclasses import dataclass


@dataclass
class RootFSInfo:
    major: int
    minor: int
    disk: str


""" A simple class for OT3 RootFS manipulation
 ** Get current partition RootFS is mounted on
 ** Swap RootFS partition
 ** Factory reset OT3 using bmap image on SD-Card """


class RootFS:
    @dataclass
    class RootFSConfig:
        """ CONFIG vars, can be changed through the commandline arguments """
        ROOTFS_PART1: str = ''
        ROOTFS_PART2: str = ''
        BMAP_IMAGE: str = ''
        BMAP_FILE: str = ''
        DISK: str = 'mmcblk0'
        BOOT_SRC_CARVE_OUT: str = ''
        ROOT_FS_PARTITION: str = ''
        SD_CARD_MOUNT_POINT: str = '/media/mmcblk1p1'

    def __init__(self):
        self.root_FS_config_ = self.RootFSConfig('' , '', '' , '',
                                                 'mmcblk0',
                                                 '', '', '/media/mmcblkp1')

    def set_partition(self, arg, partition_name):
        """ Run boot util command here to set partion
         Use the libubootenv utility to set bootargs
         boot.src has a carveout for bootargs, use that """
        self.BootFSConfig_.BOOT_SRC_CARVE_OUT = arg.bco

        subprocess.run(["fw_setenv", self.root_FS_config_.BOOT_SRC_CARVE_OUT,
                        "boot="+partition_name])

    def get_partition(self) -> RootFSInfo:
        """ print partition name"""
        dev = os.stat('/')[stat.ST_DEV]
        major = os.major(dev)
        minor = os.minor(dev)
        out = subprocess.Popen(shlex.split("df /"),
                               stdout=subprocess.PIPE).communicate()
        m = re.search(r'(/[^\s]+)s', str(out))
        if m is not None:
            mp = m.group(1)
            ri = RootFSInfo(major, minor, mp)
            return ri
        else:
            raise AssertionError("Unexpected value of partition")

    def swap_partition(self, arg):
        """swap partitions get current partition
           and swap it with the other available partition"""
        current_partition = self.get_partition()
        if current_partition is not None:
            if current_partition.disk == self.root_FS_config_.ROOTFS_PART1:
                self.set_partition(arg, self.root_FS_config_.ROOTFS_PART2)
            else:
                self.set_partition(arg, self.root_FS_config_.ROOTFS_PART1)

    def factory_restore(self, arg):
        """" bmap to factory reset here"""
        bmap = (self.root_FS_config_.SD_CARD_MOUNT_POINT +
                self.root_FS_config_.BMAP_FILE)
        bmap_img = (self.root_FS_config_.SD_CARD_MOUNT_POINT +
                    self.root_FS_config_.BMAP_IMAGE)
        subprocess.run(["bmaptool", "copy", "--bmap", bmap ,
                        "--no-sig-verify", "--no-verify",
                        bmap_img,
                        self.root_FS_config_.DISK])

    """ debug fuctions """
    def print_rootFS_partition(self, arg) -> str:
        tmp = self.get_partition()
        return ('Current RootFS Partition '+tmp.disk+'\n')

    def print_rootFS_config(self, arg) -> str:
        return(('ROOTFS_TEST_TITLE '+arg.tt+'\n') +
               ('ROOTFS_PART1 '+self.root_FS_config_.ROOTFS_PART1+'\n') +
               ('ROOTFS_PART2 '+self.root_FS_config_.ROOTFS_PART2+'\n') +
               ('BMAP_IMAGE '+self.root_FS_config_.BMAP_IMAGE+'\n') +
               ('BMAP_FILE '+self.root_FS_config_.BMAP_FILE+'\n') +
               ('DISK '+self.root_FS_config_.DISK+'\n') +
               ('BOOT_SRC_CARVE_OUT '+self.root_FS_config_.BOOT_SRC_CARVE_OUT+'\n') +
               ('ROOT_FS_PARTITION '+self.root_FS_config_.ROOT_FS_PARTITION+'\n') +
               ('SD_CARD_MOUNT_POINT '+self.root_FS_config_.SD_CARD_MOUNT_POINT+'\n')
               )

    def debug(self, arg):
        print(self.print_rootFS_partition(arg))
        print(self.print_rootFS_config(arg))