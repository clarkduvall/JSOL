read_file:def(file) {
   data:read(file 512)
   if >(len(data) 0) {
      print(data)
      read_file(file)
   }
}
main:def() {
   import("file")
   print("Enter the file you would like to see: ")
   filename:read(0 128)
   fd:open(filename)
   println()
   read_file(fd)
   close(fd)
}
