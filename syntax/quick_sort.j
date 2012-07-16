qsort|def(l c) {
   if >(len(l) 1) {
      p|l(0)
      lo|qsort(filter(def(x) { c(p x) } l) c)
      hi|qsort(filter(def(x) { c(x p) } l) c)
      eq|filter(def(x) { =(p x) } l)
      +(lo eq hi)
   } else {
      l
   }
}

main|def() {
   println("Unsorted:          " l|[2 23 6 1 26 923 5 0 92])
   println("Sorted high to low:" qsort(l <))
   println("Sorted low to high:" qsort(l >))
}
