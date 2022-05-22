import heapq

#A = [3,5,1,2,0]
A = [1, 6, 8, 0, -1]

#print(A)
#heapq.heapify(A)
#print(A)

heapq.heappush(A,-5)
heapq.heappush(A,-3)
for k in A:
    print(heapq.heappop(A))


B = [(1, 2, 3), (2, 1, 0), (0, 2, 3), (-1, 10, 5), (-2, 1, 3)]
heapq.heapify(B)
for k in B:
    print(heapq.heappop(B))
