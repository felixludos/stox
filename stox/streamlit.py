from collections import Counter
import streamlit as st
from streamlit_elements import elements, dashboard, mui, editor, media, lazy, sync, nivo

from .general import country_flags, sector_emojis, sector_colors


class Portfolio:
	def __init__(self):
		self.max_weight = 100.
		self.cards = None
		self.ascending = False
		self.upper_limit = False
		self.sectors = None
		self.countries = None
		self.stats = None

	def populate(self, cards):
		self.max_weight = max(10., min(float(int(420 / len(cards))//10*10), 100.))
		for c in cards:
			c.weight = 100/len(cards)
			c.max_weight = self.max_weight
			c.set_portfolio(self)
		self.cards = cards
		self.sectors = [k for k, v  in Counter(c.sector for c in cards).most_common()]
		self.countries = [k for k, v  in Counter(c.country for c in cards).most_common()]
		self.stats = list(cards[0].features)

	def update_weight(self, card, new_value):
		other = [c for c in self.cards if c != card and not c.locked]
		delta = card.weight - new_value
		fixed = sum(c.weight for c in self.cards if c.locked)
		current = sum(c.weight for c in other)

		if not len(other):
			st.error(f'Cannot update weight of {card.name} because it is the only unlocked card.')

		for c in other:
			new = c.weight + delta * (1/len(other) if current == 0 else c.weight / current)
			c.weight = min(max(0., new), 100.)

		card.weight = 100 - (fixed + sum(c.weight for c in other))

	def _select_all(self):
		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				num_sel += 1
				if not c.selected:
					num_new += 1
				c.selected = True
		st.toast(f'Selected {num_sel} stocks ({num_new} new)')

	def _deselect_all(self):
		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				num_sel += 1
				if c.selected:
					num_new += 1
				c.selected = False
		st.toast(f'Deselected {num_sel} stocks ({num_new} new)')

	def _invert_selection(self):
		num_sel = 0
		for c in self.cards:
			if not c.hidden:
				c.selected = not c.selected
				if c.selected:
					num_sel += 1
		st.toast(f'Inverted selection ({num_sel} selected)')

	def _show_all(self):
		num_new = 0
		for c in self.cards:
			if c.hidden:
				num_new += 1
			c.hidden = False
			c.selected = False
		st.toast(f'Showing all ({num_new} were hidden)')

	def _hide_selected(self):
		num_hidden = 0
		for c in self.cards:
			if c.selected:
				num_hidden += 1
				c.hidden = True
				c.selected = False
		st.toast(f'{num_hidden} stocks hidden')

	def _lock_hidden(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if c.hidden:
				num_locked += 1
				if not c.locked:
					num_new += 1
				c.locked = True
		st.toast(f'Locked {num_locked} stocks ({num_new} new)')

	def _lock_selected(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if not c.hidden and c.selected:
				num_locked += 1
				if not c.locked:
					num_new += 1
				c.locked = True
		st.toast(f'Locked {num_locked} stocks ({num_new} new)')

	def _unlock_selected(self):
		num_locked, num_new = 0, 0
		for c in self.cards:
			if not c.hidden and c.selected:
				num_locked += 1
				if c.locked:
					num_new += 1
				c.locked = False
		st.toast(f'Unlocked {num_locked} stocks ({num_new} new)')

	def _sort_by_weight(self):
		self.cards.sort(key=lambda c: c.weight, reverse=not self.ascending)

	def _toggle_sort_order(self):
		self.ascending = not self.ascending

	def _toggle_bound(self):
		self.upper_limit = not self.upper_limit

	def _apply_selection(self, select_sectors, select_country, select_stat):

		sectors = [s for s in select_sectors if s in self.sectors]
		countries = [c for c in select_country if c in self.countries]
		stat = select_stat if select_stat in self.stats else None

		num_sel, num_new = 0, 0
		for c in self.cards:
			if not c.hidden:
				sector, country = c.sector, c.country
				if ((len(sectors) and sector not in sectors) or (len(countries) and country not in countries)
						or ()):
					if not c.selected:
						num_new += 1
					c.selected = True
					num_sel += 1
				if len(countries) and country not in countries:
					c.hidden = True
				if stat is not None:
					val = c.features[stat]
					if val is None:
						c.hidden = True
					elif self.upper_limit and val > st.session_state['weight']:
						c.hidden = True
				if not c.hidden:
					c.selected = True


	def _apply_sort(self, group_sector, group_country, group_stat):
		# st.write(f'Sorting by {group_sector} and {group_country} and {group_stat}')

		sectors = [s for s in group_sector if s in self.sectors]
		countries = [c for c in group_country if c in self.countries]
		stat = group_stat if group_stat in self.stats else None

		def key(card):
			sector, country = card.sector, card.country
			terms = []
			if stat is not None:
				val = card.features[stat]
				if val is None:
					val = (-1)**(self.ascending) * float('inf')
				terms.append(val)
			if len(sectors):
				terms.append(tuple(sector == s for s in sectors))
			if len(countries):
				terms.append(tuple(country == c for c in countries))
			return tuple(terms)
		self.cards.sort(key=key, reverse=not self.ascending)


	def display(self):
		with st.sidebar:

			st.header(f'Controls')

			col1, col2, col3, col4 = st.columns(4)
			with col1:
				st.button('🔶 all', help='Select all', on_click=self._select_all)
			with col2:
				st.button('⬛ all', help='Deselect all', on_click=self._deselect_all)
			with col3:
				st.button('🔄 all', help='Invert selection', on_click=self._invert_selection)
			with col4:
				st.button('Show all', help='Show all hidden', on_click=self._show_all) # 👁

			col1, col2, col3, col4 = st.columns(4)
			with col1:
				st.button('🔒🔶', help='Lock selected', on_click=self._lock_selected)
			with col2:
				st.button('🔓🔶', help='Unlock selected', on_click=self._unlock_selected)
			with col3:
				st.button('💭🔶', help='Hide selected', on_click=self._hide_selected)
			with col4:
				st.button('🔒💭', help='Lock all hidden', on_click=self._lock_hidden)

			hidden = [c for c in self.cards if c.hidden]
			st.write(f'Showing {len(self.cards) - len(hidden)} of {len(self.cards)} stocks.')

			col1, col2 = st.columns(2)
			with col1:
				st.header(f'Sort')
			with col2:
				st.button('by weight', help='Sort by weight', on_click=self._sort_by_weight)

			with st.form('sort_form', clear_on_submit=True):
				group_sector = st.multiselect('Group sector', self.sectors, key='group_sector')
				group_country = st.multiselect('Group country', self.countries, key='group_country')
				group_stat = st.selectbox('by Stat', ['', *self.stats], key='group_stat')

				# print(f'{group_sector}, {st.session_state.get("group_sector", None)}')

				col1, col2 = st.columns([1,2])
				with col1:
					sort_cards = st.form_submit_button('Apply')
				with col2:
					st.button('🔼' if self.ascending else '🔽',
							  help='Sort ascending/descending', on_click=self._toggle_sort_order)

			if sort_cards:
				self._apply_sort(group_sector, group_country, group_stat)

			st.header(f'Selection')
			with st.form('select_form', clear_on_submit=True):
				select_sectors = st.multiselect('Select sectors', self.sectors)
				select_country = st.multiselect('Select country', self.countries)
				select_stat = st.selectbox('Feature', ['Weight', *self.stats])

				d_col, q_col = st.columns([1, 5])
				# with d_col:
				# 	st.button('↘️' if self.upper_limit else '↗️', help='Select higher/lower than limit',)
				with q_col:
					st.number_input('Weight', 0., self.max_weight, None, label_visibility='collapsed')

				select_cards = st.form_submit_button('Apply')

			if select_cards:
				self._apply_selection(select_sectors, select_country, select_stat)

		# st.set_page_config(layout='wide')

		# print()
		# if 'sidebar_state' not in st.session_state:
		# 	st.session_state.sidebar_state = 'expanded'


		stock_col, viz_col = st.columns([1, 2 if st.session_state.sidebar_state == 'expanded' else 3])

		with stock_col:
			st.header('Cards')
			for card in self.cards:
				if not card.hidden:
					card.display()

		with viz_col:
			st.write(f'Total weight: {sum(card.weight for card in self.cards):.2f}')




		# layout = [
		#     dashboard.Item("cards", 0, 0, 6, 4),
		# ]
		# with elements("demo"):
		# 	with dashboard.Grid(layout, draggableHandle=".draggable"):
		# 		with mui.Card(key="cards", sx={"display": "flex", "flexDirection": "column"}):
		# 			mui.CardHeader(title="Cards", className="draggable")
		# 			with mui.CardContent(sx={"flex": 1, "minHeight": 4, 'minWidth': 3}):
		#
		# 				mui.Typography("Hello world")
		#
		# 			with mui.CardActions:
		# 				mui.Button("Apply changes")

			# st.title('Stocks')
			# for card in self.cards:
			# 	if not card.hidden:
			# 		card.display()



class Card:
	def __init__(self, info, features, max_weight=100.):
		self.info = info
		self.features = features
		self.p = None
		self.weight = 1.
		self.max_weight = 100.
		self.locked = False
		self.selected = False
		self.hidden = False

	@property
	def name(self):
		return self.info['company_name']
		# return self.info['ticker']

	@property
	def sector(self):
		return str(self.info['sector'])

	@property
	def country(self):
		return str(self.info['country'])

	def set_portfolio(self, portfolio):
		self.p = portfolio

	def toggle_lock(self):
		self.locked = not self.locked

	def toggle_select(self):
		self.selected = not self.selected
		# st.write(f'{self.name} is selected: {self.selected}')

	def update_weight(self):
		self.p.update_weight(self, float(st.session_state[f'weight_{self.name}']))
		return self.weight

	def display(self):
		with st.container():
			title = self.name
			terms = []
			if self.country in country_flags:
				terms.append(country_flags[self.country])
			if self.sector in sector_emojis:
				terms.append(sector_emojis[self.sector])
			terms.append(self.name)
			title = ' '.join(terms)

			with st.expander(title):
				st.write(f'Details for {self.info["company_name"]}')

			s_col, w_col, l_col = st.columns([1, 3, 1])

			with s_col:
				st.button('🔶' if self.selected else '⬛', key=f'select_{self.name}', on_click=self.toggle_select)
			with w_col:
				st.slider('Weight', 0., self.max_weight,
										self.weight,
										key=f'weight_{self.name}',
										disabled=self.locked, on_change=self.update_weight, label_visibility='collapsed')
				# st.markdown(f'<p style="color:#333;">{self.name}</p>', unsafe_allow_html=True)
			with l_col:
				st.button('🔓' if self.locked else '🔒', key=f'lock_{self.name}', on_click=self.toggle_lock)

			# st.divider()











