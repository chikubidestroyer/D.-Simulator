// Dijkstra implementation in C++ that Yuxiang Lin wrote before he took this course.
// This is only used for testing the correctness of the SQL implementation.

#include <bits/stdc++.h>

const int maxN = 5000;
int to[maxN], pre[maxN], last[maxN], cost[maxN], dist[maxN];
bool visited[maxN];

void dijkstra(int src)
{
	dist[src] = 0;
	std::priority_queue<std::pair<int, int>,
						std::vector<std::pair<int, int> >,
						std::greater<std::pair<int, int> > > heap;
	heap.push(std::make_pair(dist[src], src));

	while (!heap.empty())
	{
		int v(heap.top().second);
		heap.pop();
		if (visited[v])	continue;
		visited[v] = true;

		for (int nxt(last[v]); nxt; nxt = pre[nxt])
		{
			if (!visited[to[nxt]] && dist[to[nxt]] > dist[v] + cost[nxt])
			{
				dist[to[nxt]] = dist[v] + cost[nxt];
				heap.push(std::make_pair(dist[to[nxt]], to[nxt]));
			}
		}
	}
}

int main()
{
	int n, m;
	std::cin >> n >> m;
	int u, v, w;
	int e = 0;
	for (int i = 0; i < m; ++i)
	{
		std::cin >> u >> v >> w;
		++e;
		to[e] = v;
		pre[e] = last[u];
		last[u] = e;
		cost[e] = w;
	}

	memset(dist, 0x7f, sizeof(dist));
	dijkstra(0);

	for (int i = 0; i < n; ++i) std::cout << i << ": " << dist[i] << '\n';
	return 0;
}
