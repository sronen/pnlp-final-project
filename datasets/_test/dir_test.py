#ufnamedir_test.py

UNI_ENC = "unicode-escape"

from os import listdir

def write_dir_contents(dirname, outfile):

	fout = open(outfile, "w")

	fnames = listdir(dirname)
	fnames.remove(".DS_Store")

	for fn in fnames: 
		fn_to_write = fn.decode(UNI_ENC) if not isinstance(fn, unicode) else fn
		fout.write(fn_to_write.encode(UNI_ENC) + "\n")

	fout.close()

if __name__ == "__main__":
	write_dir_contents("pt", "pt_reg.txt")
	write_dir_contents(u"pt", "pt_uni.txt")

